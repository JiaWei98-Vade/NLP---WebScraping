import requests
from bs4 import BeautifulSoup
from collections import Counter
import json
import re
from urllib.parse import urljoin

# Declare all_text as a global variable
all_text = ''
# Declare links as a global list
links = []


def check_url_response(url):
    # Send a GET request to the website
    response = requests.get(url)   
    return response

def get_content(response):
    # Parse the HTML content of the webpage
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def links_retriever(soup):
    global links  # Declare links as a global variable
    links = soup.find_all('a')

def topic_reader(soup):
    # Extract the topic from the article content
    return soup.find('h1', class_='article__title').get_text()

def paragraph_reader(soup):
    global all_text
    # Find all the paragraphs in the article      
    all_paragraphs = soup.find_all('p')
    all_text += ' '.join(paragraph.get_text() for paragraph in all_paragraphs)

def links_reader(link):
    # Check if the link has text and is not a relative path
    if link.text and link.get('href') and not link.get('href').startswith('#'):
        link_url = link.get('href')
        if not bool(re.match(r'https?://', link_url)):
            link_url = urljoin(url, link_url)  # Handle relative paths
        link_response = check_url_response(link_url)
    return link_response

def punctuation_remover():
    global all_text
    # Extract the most common subject and its company domain
    punctuations = '''\r\n!()-[]{};:'"”\, <>./?@#$%^&*_~'''
    all_text = all_text.lower()
    for character in all_text:
        if character in punctuations:
            all_text = all_text.replace(character, ' ')
        if character == 'x':
            all_text = all_text.replace(character, 'X')
            
def stopword_remover(tokens):
    # Retrieve stopwords from a URL
    stopwords_url = 'https://raw.githubusercontent.com/theleadio/datascience_demo/master/stopwords.txt'
    response_stopwords = requests.get(stopwords_url)
    stopwords = response_stopwords.text.splitlines()
    return [t for t in tokens if t not in stopwords]
            
def get_token():
    punctuation_remover()
    tokens_filtered = stopword_remover(all_text.split())
    counter_desc = Counter(tokens_filtered).most_common(10)
    for token in counter_desc:
        name = token[0]
        domain = token[0].lower() + '.com'
        subject_url_token = 'https://'+ domain
        response = check_url_response(subject_url_token)
        
        if response.status_code == 200:
            company_data.append({"company_name": name, "company_domain": domain})
            break

def get_subject_domain():
    for link in links:
        reponse_link= links_reader(link)
        if reponse_link.status_code == 200:
            # Parse the HTML content of the webpage
            soup = get_content(reponse_link)
            paragraph_reader(soup)
            
    get_token()
    
def reg_exp_url_match():
    for link in links:
        href = link.get('href')
                    
        if href and re.match(r'^https?://[a-z]+\.([a-z]+)+(\.[a-z]+)', href):
            match = re.match(r'^https?://[a-z]+\.([a-z]+)+(\.[a-z]+)', href)
            if match and match.group(1) != 'techcrunch':              
                company_name = match.group(1).capitalize()
                company_domain = match.group(1) + match.group(2) 
                company_data.append({"company_name": company_name, "company_domain": company_domain})
                break
    
               
# Provide the URL of the website
url = 'https://techcrunch.com/2023/10/27/x-is-launching-new-premium-and-basic-subscription-tiers/'
response = check_url_response(url)

# Check if the request was successful
if response.status_code == 200:
    # Find all the links in the article
    company_data = []  
    soup = get_content(response)
    links_retriever(soup)
    paragraph_reader(soup)
    topic = topic_reader(soup)
    
    get_subject_domain()
    reg_exp_url_match()
    
    # Create the JSON structure
    data = {"related_companies": company_data[:2], "topic": topic}

    # Convert the data to JSON and print it
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)
    
    with open('domain_results.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

else:
    print('Failed to retrieve the webpage. Status code:', response.status_code)
