import aiohttp
import asyncio
from aiohttp_socks import ProxyType, ProxyConnector
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import csv
import os
import secrets
import string
from fake_useragent import UserAgent
from colorama import init, Fore

# Initialize colorama
init()

TEMP_DB_PATH = 'temp'
DATA_DIRECTORY = 'archive'
CSV_FILE_PATH = os.path.join('data', 'data.csv')


def print_colored(message, color=Fore.WHITE):
    print(color + message + Fore.RESET)


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text()


def get_random_user_agent():
    user_agent = UserAgent()
    return user_agent.random


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
    print_colored(f"Data saved to: {filepath}", Fore.MAGENTA)


def save_url_to_csv(filename, url):
    with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'url', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not os.path.exists(CSV_FILE_PATH):
            writer.writeheader()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        writer.writerow(
            {'filename': filename, 'url': url, 'timestamp': timestamp})
        print_colored(
            f"URL saved to CSV: filename={filename}, url={url}", Fore.MAGENTA)


def save_url_to_temp_db(url):
    os.makedirs(TEMP_DB_PATH, exist_ok=True)
    temp_db_file = os.path.join(TEMP_DB_PATH, "scraped.txt")

    # Check if the URL is already in the database
    if url in load_urls_from_temp_db():
        print_colored(
            f"URL already in temporary database: {url}", Fore.MAGENTA)
        return

    with open(temp_db_file, 'a', encoding='utf-8') as file:
        file.write(f"{url}\n")
    print_colored(f"URL saved to temporary database: {url}", Fore.MAGENTA)


def load_urls_from_temp_db():
    urls_set = set()
    temp_db_file_path = os.path.join(TEMP_DB_PATH, "scraped.txt")
    if os.path.exists(temp_db_file_path):
        with open(temp_db_file_path, 'r', encoding='utf-8') as file:
            urls_set.update(line.strip() for line in file if line.strip())
    return urls_set


async def web_crawler_with_saving_and_urls(id, url, session, connector):
    flag = False
    if ".onion" in str(url) or ".i2p" in str(url):
        flag = True
    if not flag:
        return set()
    if not id:
        id = 1
    scraped_urls = load_urls_from_temp_db()
    if url in scraped_urls:
        print_colored(f"URL already scraped: {url}", Fore.MAGENTA)
        return set()

    try:
        # Add a random user agent to the headers
        headers = {'User-Agent': get_random_user_agent()}
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            response.raise_for_status()  # Raise an HTTPError for bad responses

            if response.status == 200:
                # Get the final URL after following redirects
                final_url = str(response.url)
                print_colored(
                    f"Final URL after redirects: {final_url}", Fore.MAGENTA)

                soup = BeautifulSoup(await response.text(), 'html.parser')
                base_url = final_url
                urls_set = {
                    urljoin(base_url, link.get('href'))
                    for link in soup.find_all('a', href=True)
                    if not link.get('href').startswith('mailto:')
                }
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f"{id}_{timestamp}_{generate_secure_random_string(8)}.html"
                save_data_to_file(await response.text(), DATA_DIRECTORY, filename)
                # Save the final URL to CSV
                save_url_to_csv(filename, final_url)
                # Save the final URL to the temporary database
                save_url_to_temp_db(final_url)
                save_url_to_temp_db(url)
                return urls_set
            else:
                print_colored(
                    f"Failed to retrieve the page. Status code: {response.status}", Fore.MAGENTA)
                return set()

    except Exception as e:
        print_colored(
            f"Request failed for URL: {url}\nError: {e}", Fore.MAGENTA)
        return set()


async def recursive_crawler(url, session, connector, depth=1, max_depth=3, limit=False):
    if limit and depth > max_depth:
        return

    print_colored(f"\nCrawling URL (Depth {depth}): {url}", Fore.MAGENTA)
    found_urls = await web_crawler_with_saving_and_urls(depth, url, session, connector)

    tasks = [recursive_crawler(next_url, session, connector,
                               depth + 1, max_depth, limit) for next_url in found_urls]
    await asyncio.gather(*tasks)


async def main():
    test_url = "http://ramble.i2p/"
    url_to_crawl = test_url
    proxy_url = 'http://localhost:4444'

    connector = ProxyConnector.from_url(proxy_url)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            await recursive_crawler(url_to_crawl, session=session, connector=connector)
    except KeyboardInterrupt:
        print_colored("KeyboardInterrupt received. Exiting...", Fore.RED)
    finally:
        temp_folder_path = 'temp'
        try:
            for file_name in os.listdir(temp_folder_path):
                file_path = os.path.join(temp_folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)

            os.rmdir(temp_folder_path)
        except Exception as e:
            print_colored(f"Error during cleanup: {str(e)}", Fore.MAGENTA)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\nKeyboardInterrupt received. Exiting...", Fore.RED)
