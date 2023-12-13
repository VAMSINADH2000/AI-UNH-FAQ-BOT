
from langchain.chains import RetrievalQA
import os
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import find_dotenv, load_dotenv
import pinecone
import nest_asyncio
from pymongo import MongoClient
nest_asyncio.apply()
from flask import Flask, render_template, request, jsonify

# Load your env variables
load_dotenv(find_dotenv())
# DB Configuration
client = MongoClient('mondb_url')
chat_db = client['UNH_chat_bot']
conversations = chat_db['conversations'] 

def insert_data(query,bot_response,db=conversations):
    conversation = {
        "query": query,
        "bot_response": bot_response,
    }
    db.insert_one(conversation)
    print("Data inserted")


def configure():
    nest_asyncio.apply()
    pinecone.init(
        api_key=os.environ['PINECONE_API_KEY'],  
        environment=os.environ['PINECONE_ENVIRONMENT'] 
    )
    print("Configuration Successful")


configure()
embeddings = OpenAIEmbeddings()
docsearch = Pinecone.from_existing_index(os.environ['PINECONE_INDEX'], embeddings)
llm=OpenAI()
qa_with_sources = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever(), return_source_documents=True)

def query(question):
    result = qa_with_sources({"query": question})
    return result




app = Flask(__name__)

@app.route("/")
def index():

    return render_template('chat.html')




@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form["msg"]
        result = query(msg)
        
        # Since result['result'] is a string, you can use it directly
        response_text = result['result'] if result['result'] else "Sorry, I didn't understand that."
        
        # Create a response dictionary to send back to the client
        response_dict = {"data": response_text}

        # Getting Source links
        sources = {}
        source_num = 1
        for i in result['source_documents']:
            sources["source"+str(source_num)] = i.metadata['source']
            source_num+=1

        response_dict['sources'] = sources
        insert_data(query=msg,bot_response=response_dict)

        return jsonify(response_dict)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"data": "An error occurred while processing the request."})


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000,debug=True)





