import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def save_data_to_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(data)
    print(f"Data saved to: {filepath}")

def web_crawler_with_saving(url, data_directory='data'):
    # Send an HTTP request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract information or perform actions based on your needs
        # For example, print the titles of all the links on the page
        for link in soup.find_all('a'):
            print(link.get('title', 'No title attribute'))

        # Save the entire HTML content to a file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{url.replace('://', '_').replace('/', '_')}_{timestamp}.html"
        save_data_to_file(response.text, data_directory, filename)

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# Example usage
url_to_crawl = "https://google.com"
web_crawler_with_saving(url_to_crawl)
