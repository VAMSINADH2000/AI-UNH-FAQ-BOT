import os 
import nest_asyncio
import pinecone 
from langchain.document_loaders.sitemap import SitemapLoader
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import find_dotenv, load_dotenv

# Load your env variables
load_dotenv(find_dotenv())

with open('url_mapping.json', 'r', encoding='utf-8') as file:
    url_mapping = json.load(file)

def configure():
    # os.environ["OPENAI_API_KEY"] = "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"
    nest_asyncio.apply()
    pinecone.init(
        api_key="32cd518f-0750-472d-919a-8a0ec30ff796",  
        environment="us-west1-gcp"  
    )
    print("Configuration Successful")
    


def webscrap(sitemap_url = "https://www.newhaven.edu/sitemap.xml"):
    response = requests.get(sitemap_url)
    keywords = [
        "data-science",
        "Artificial",
        "intelligence",
        "faq",
        "tagliatela",
        "international",
        "immigration",
        "visa",
        "international-services",
        "course",
        "bursars",
        "one-stop",
        "registrar"
    ]
    soup = BeautifulSoup(response.content, 'xml')
    urls = [element.text for element in soup.find_all('loc')]
    urls = [url for url in urls if any(keyword.lower() in url.lower() for keyword in keywords)]
    pdf_urls = [url for url in urls if url.lower().endswith('.pdf')]
    php_urls = [url for url in urls if url.lower().endswith('.php')]
    return pdf_urls, php_urls


def is_valid_url(url):
    """
    Checks if the URL is a valid HTTP or HTTPS URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def download_pdf(url, folder="PDFs"):
    """
    Downloads a single PDF file from a URL.
    """
    if not os.path.isdir(folder):
        os.makedirs(folder)

    try:
        response = requests.get(url, stream=True)
        
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            filename = os.path.join(folder, url.split('/')[-1] or "downloaded_pdf.pdf")

            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Successfully downloaded {url}")
        else:
            print(f"Failed to download {url} - Response code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")



def loadDataFrmPhpUrls(php_urls):
    try:
        sitemap_loader = SitemapLoader(web_path="https://www.newhaven.edu/sitemap.xml",
                                    filter_urls=php_urls)
        docs = sitemap_loader.load()
        print("Php Data Loaded successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
    return docs





def loadPDFData():
    pdf_data = []
    cwd = os.getcwd()
    for pdf in os.listdir('PDFs'):
        pdf_path = os.path.join(cwd, 'PDFs')
        pdf = os.path.join(pdf_path,pdf)
        loader = PyPDFLoader(pdf)
        pages = loader.load_and_split()
        for page in pages:
            source = page.metadata['source'].split('/')[-1]
            page.metadata['source'] = url_mapping[source]
        pdf_data.extend(pages)
    print("PDF Data Loaded successfully")
    return pdf_data


def split_data_chunks(final_data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1200,
        chunk_overlap  = 200,
        length_function = len,
    )
    docs_chunks = text_splitter.split_documents(final_data)
    print("Splitting Data Done Successfully")
    return docs_chunks



def write_data_to_database(index_name,data):
    print("Writing Data to Vector Database")
    embeddings = OpenAIEmbeddings()
    docsearch = Pinecone.from_documents(data, embeddings, index_name=index_name)
    print("Data Written successfully")



# Inference
configure()
pdf_urls,php_urls = webscrap()
print("PHP URLs:",len(php_urls))
print("PDF URLs:",len(pdf_urls))

php_data = loadDataFrmPhpUrls(php_urls)
pdf_data = loadPDFData()
final_data = []
final_data.extend(php_data)
final_data.extend(pdf_data)

data = split_data_chunks(final_data)
write_data_to_database(os.environ['PINECONE_INDEX'],data)