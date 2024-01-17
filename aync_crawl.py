import aiohttp
import asyncio
from aiohttp_socks import ProxyType, ProxyConnector
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import csv
import secrets
import string
import random
from fake_useragent import UserAgent

TEMP_DB_PATH = 'temp'
DATA_DIRECTORY = 'data'
CSV_FILE_PATH = os.path.join(DATA_DIRECTORY, 'data.csv')


async def get_random_user_agent():
    user_agent = UserAgent()
    return user_agent.random


async def generate_secure_random_string(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def sanitize_filename(filename):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    return ''.join(char if char not in invalid_chars else '_' for char in filename)


async def save_data_to_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, await sanitize_filename(filename))
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(data)
    print(f"Data saved to: {filepath}")


async def save_url_to_csv(filename, url):
    with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'url', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not os.path.exists(CSV_FILE_PATH):
            writer.writeheader()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        writer.writerow(
            {'filename': filename, 'url': url, 'timestamp': timestamp})
        print(f"URL saved to CSV: filename={filename}, url={url}")


async def save_url_to_temp_db(url):
    os.makedirs(TEMP_DB_PATH, exist_ok=True)
    temp_db_file = os.path.join(TEMP_DB_PATH, "scraped.txt")
    with open(temp_db_file, 'a', encoding='utf-8') as file:
        file.write(f"{url}\n")
    print(f"URL saved to temporary database: {url}")


async def load_urls_from_temp_db():
    urls_set = set()
    temp_db_file_path = os.path.join(TEMP_DB_PATH, "scraped.txt")
    if os.path.exists(temp_db_file_path):
        with open(temp_db_file_path, 'r', encoding='utf-8') as file:
            urls_set.update(line.strip() for line in file)
    return urls_set


async def web_crawler_with_saving_and_urls(id, url, session):
    if not id:
        id = 1
    scraped_urls = await load_urls_from_temp_db()
    if url in scraped_urls:
        print(f"URL already scraped: {url}")
        return set()

    try:
        # Add a random user agent to the headers
        headers = {'User-Agent': await get_random_user_agent()}
        proxies = {
            'http': 'socks5h://localhost:9050',
            'https': 'socks5h://localhost:9050'
        }
        # Use the session to handle redirects
        async with session.get(url, headers=headers, allow_redirects=True, proxies=proxies) as response:
            response.raise_for_status()  # Raise an HTTPError for bad responses

            if response.status == 200:
                # Get the final URL after following redirects
                final_url = str(response.url)
                print(f"Final URL after redirects: {final_url}")

                soup = BeautifulSoup(await response.text(), 'html.parser')
                base_url = final_url
                urls_set = {
                    urljoin(base_url, link.get('href'))
                    for link in soup.find_all('a', href=True)
                    if not link.get('href').startswith('mailto:')
                }
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f"{id}_{timestamp}_{await generate_secure_random_string(8)}.html"
                await save_data_to_file(await response.text(), DATA_DIRECTORY, filename)
                await save_url_to_csv(filename, final_url)  # Save the final URL to CSV
                # Save the final URL to the temporary database
                await save_url_to_temp_db(final_url)
                await save_url_to_temp_db(url)
                return urls_set
            else:
                print(f"Failed to retrieve the page. Status code: {response.status}")
                return set()

    except aiohttp.ClientError as e:
        print(f"Request failed for URL: {url}\nError: {e}")
        return set()


async def recursive_crawler(url, depth=1, max_depth=3, limit=False):
    if limit and depth > max_depth:
        return

    print(f"\nCrawling URL (Depth {depth}): {url}")

    connector = ProxyConnector.from_url('socks5://localhost:9050')

    async with aiohttp.ClientSession(connector=connector) as session:
        found_urls = await web_crawler_with_saving_and_urls(depth, url, session)

        for next_url in found_urls:
            await recursive_crawler(next_url, depth + 1, max_depth)


# Example usage
test_url = "http://torch2cjfpa4gwrzsghfd2g6nebckghjkx3bn6xyw6capgj2nqemveqd.onion/"

# url_to_crawl = "https://lenovo.com"
url_to_crawl = test_url

# Run the asynchronous main function
asyncio.run(recursive_crawler(url_to_crawl))
