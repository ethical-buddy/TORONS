import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from multiprocessing import cpu_count, Process, Manager
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import os
import secrets
import string
from colorama import Fore, init

init()

base_torch_url = "http://torch2cjfpa4gwrzsghfd2g6nebckghjkx3bn6xyw6capgj2nqemveqd.onion/"
search_keywords = ["index", "heroin", "meth"]
proxy_url = 'socks5://localhost:9050'
data_directory = 'archive'
temp_db_path = 'temp'


def print_colored(message, color=Fore.WHITE):
    print(color + message + Fore.RESET)

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
    print_colored(f"Data saved to: {filepath}", Fore.GREEN)

def load_urls_from_temp_db():
    urls_set = set()
    temp_db_file_path = os.path.join(temp_db_path, "scraped.txt")
    if os.path.exists(temp_db_file_path):
        with open(temp_db_file_path, 'r', encoding='utf-8') as file:
            urls_set.update(line.strip() for line in file if line.strip())
    return urls_set

def save_url_to_temp_db(url):
    os.makedirs(temp_db_path, exist_ok=True)
    temp_db_file = os.path.join(temp_db_path, "scraped.txt")
    if url in load_urls_from_temp_db():
        return
    with open(temp_db_file, 'a', encoding='utf-8') as file:
        file.write(f"{url}\n")

def recursive_crawler(url, session, connector, visited_urls, depth=1, max_depth=3):
    async def crawl(current_url, current_depth):
        if current_depth > max_depth or current_url in visited_urls:
            return

        print_colored(f"Crawling (Depth {current_depth}): {current_url}", Fore.CYAN)
        visited_urls[current_url] = True

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            async with session.get(current_url, headers=headers) as response:
                if response.status != 200:
                    return
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                base_url = str(response.url)
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f"{current_depth}_{timestamp}_{generate_secure_random_string(8)}.html"
                save_data_to_file(html, data_directory, filename)
                save_url_to_temp_db(base_url)
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href.startswith('mailto:'):
                        continue
                    next_url = urljoin(base_url, href)
                    await crawl(next_url, current_depth + 1)
        except Exception as e:
            print_colored(f"Failed to crawl {current_url}: {e}", Fore.RED)

    return crawl(url, depth)

def run_keyword_crawler(keyword, shared_visited):
    async def main():
        connector = ProxyConnector.from_url(proxy_url)
        url_to_crawl = base_torch_url + "?s=" + keyword
        async with aiohttp.ClientSession(connector=connector) as session:
            await recursive_crawler(url_to_crawl, session=session, connector=connector, visited_urls=shared_visited)
    asyncio.run(main())

def start_crawlers():
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/not_found.txt', 'x', encoding='utf-8') as file:
            file.close()
    except FileExistsError:
        pass

    available_cores = cpu_count()
    print_colored(f"[+] Detected {available_cores} CPU cores. Starting crawler pool...", Fore.CYAN)

    manager = Manager()
    shared_visited = manager.dict()

    processes = []
    for keyword in search_keywords:
        p = Process(target=run_keyword_crawler, args=(keyword, shared_visited))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == '__main__':
    start_crawlers()
