import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

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
            # print(f"Successfully downloaded {url}")
        else:
            print(f"Failed to download {url} - Response code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


sitemap_url = "https://www.newhaven.edu/sitemap.xml"
response = requests.get(sitemap_url)
keywords = [
    "data-science",
    "Artificial",
    "intelligence",
    "faq",
    "tagliatela",
    "international",
    "immigration",
    "course"
]


soup = BeautifulSoup(response.content, 'xml')
urls = [element.text for element in soup.find_all('loc')]
urls = [url for url in urls if any(keyword.lower() in url.lower() for keyword in keywords)]


pdf_urls = [url for url in urls if url.lower().endswith('.pdf')]
php_urls = [url for url in urls if url.lower().endswith('.php')]

print("URLS",len(urls))
print("PHP URLs:",len(php_urls))
print("PDF URLs:",len(pdf_urls))

for pdf_url in pdf_urls:
    if is_valid_url(pdf_url):
        download_pdf(pdf_url)
    else:
        print(f"Invalid URL: {pdf_url}")

