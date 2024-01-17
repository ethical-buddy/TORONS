import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import csv
import secrets
import string

if os.path.exists('temp/scraped.txt'):
    os.remove('temp/scraped.txt')

if os.path.exists('data/data.csv'):
    os.remove('data/data.csv')


def generate_secure_random_string(length=8):
    alphabet = string.ascii_letters + string.digits
    secure_random_string = ''.join(secrets.choice(alphabet)
                                   for _ in range(length))
    return secure_random_string


def sanitize_filename(filename):
    # Replace invalid characters with underscores
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def save_data_to_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(data)
    print(f"Data saved to: {filepath}")


def save_url_to_csv(filename, url, csv_file='data/data.csv'):
    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'url', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not os.path.exists(csv_file):
            writer.writeheader()

        writer.writerow({'filename': filename, 'url': url})
        print(f"URL saved to CSV: filename={filename}, url={url}")


def save_url_to_temp_db(url, temp_db_path='temp'):
    os.makedirs(temp_db_path, exist_ok=True)
    temp_db_file = os.path.join(temp_db_path, f"scraped.txt")
    with open(temp_db_file, 'a', encoding='utf-8') as file:
        file.write(f"{url}\n")
    print(f"URL saved to temporary database: {url}")


def load_urls_from_temp_db(temp_db_path='temp'):
    if not os.path.exists(temp_db_path):
        return set()
    urls_set = set()
    for temp_db_file in os.listdir(temp_db_path):
        temp_db_file_path = os.path.join(temp_db_path, temp_db_file)
        with open(temp_db_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                urls_set.add(line.strip())
    return urls_set


def web_crawler_with_saving_and_urls(id, url, data_directory='data', temp_db_path='temp'):
    # Load already scraped URLs
    scraped_urls = load_urls_from_temp_db(temp_db_path)

    # Check if the URL has already been scraped
    if url in scraped_urls:
        print(f"URL already scraped: {url}")
        return set()

    # Send an HTTP request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract information or perform actions based on your needs
        # For example, print the absolute URLs of all the links on the page
        base_url = response.url
        urls_set = set()
        for link in soup.find_all('a'):
            relative_url = link.get('href')
            if relative_url:
                absolute_url = urljoin(base_url, relative_url)
                urls_set.add(absolute_url)

        # Save the entire HTML content to a file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{id}_{timestamp}_{generate_secure_random_string(8)}.html"
        save_data_to_file(response.text, data_directory, filename)

        # Save the URL, id, and timestamp to the CSV file
        save_url_to_csv(filename, url)

        # Save the URL to the temporary database
        save_url_to_temp_db(url, temp_db_path)

        return urls_set

    else:
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")
        return set()


def crawl_urls_set(urls_set, data_directory='data', temp_db_path='temp'):
    for url_id, url in enumerate(urls_set, start=1):
        print(f"\nCrawling URL: {url}")
        web_crawler_with_saving_and_urls(
            url_id, url, data_directory, temp_db_path)


# Example usage
url_to_crawl = "https://wikipedia.com"
found_urls = web_crawler_with_saving_and_urls(1, url_to_crawl)

# Print the found URLs
print("Found URLs:")
for url in found_urls:
    print(url)

# Rerun crawlers on each URL in urls_set
crawl_urls_set(found_urls)
