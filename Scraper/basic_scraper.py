import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import csv
import secrets
import string

TEMP_DB_PATH = 'temp'
DATA_DIRECTORY = 'data'
CSV_FILE_PATH = os.path.join(DATA_DIRECTORY, 'data.csv')


def generate_secure_random_string(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def sanitize_filename(filename):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    return ''.join(char if char not in invalid_chars else '_' for char in filename)


def save_data_to_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, sanitize_filename(filename))
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(data)
    print(f"Data saved to: {filepath}")


def save_url_to_csv(filename, url):
    with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'url', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not os.path.exists(CSV_FILE_PATH):
            writer.writeheader()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        writer.writerow({'filename': filename, 'url': url, 'timestamp': timestamp})
        print(f"URL saved to CSV: filename={filename}, url={url}")


def save_url_to_temp_db(url):
    os.makedirs(TEMP_DB_PATH, exist_ok=True)
    temp_db_file = os.path.join(TEMP_DB_PATH, "scraped.txt")
    with open(temp_db_file, 'a', encoding='utf-8') as file:
        file.write(f"{url}\n")
    print(f"URL saved to temporary database: {url}")


def load_urls_from_temp_db():
    urls_set = set()
    temp_db_file_path = os.path.join(TEMP_DB_PATH, "scraped.txt")
    if os.path.exists(temp_db_file_path):
        with open(temp_db_file_path, 'r', encoding='utf-8') as file:
            urls_set.update(line.strip() for line in file)
    return urls_set


def web_crawler_with_saving_and_urls(id, url):
    scraped_urls = load_urls_from_temp_db()
    if url in scraped_urls:
        print(f"URL already scraped: {url}")
        return set()

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = response.url
        urls_set = {urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)}

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{id}_{timestamp}_{generate_secure_random_string(8)}.html"
        save_data_to_file(response.text, DATA_DIRECTORY, filename)
        save_url_to_csv(filename, url)
        save_url_to_temp_db(url)

        return urls_set
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return set()


def crawl_urls_set(urls_set):
    for url_id, url in enumerate(urls_set, start=1):
        print(f"\nCrawling URL: {url}")
        web_crawler_with_saving_and_urls(url_id, url)


# Example usage
url_to_crawl = "https://wikipedia.com"
found_urls = web_crawler_with_saving_and_urls(1, url_to_crawl)

# Print the found URLs
print("Found URLs:")
for url in found_urls:
    print(url)

# Rerun crawlers on each URL in urls_set
crawl_urls_set(found_urls)
