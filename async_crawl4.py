import asyncio
import aiohttp
import psutil
from bs4 import BeautifulSoup
from multiprocessing import Process
from urllib.parse import urljoin, urlencode
from colorama import Fore, init
from concurrent.futures import ProcessPoolExecutor
from analyse_data_mongo import add_url_to_mongo
from aiohttp_socks import ProxyConnector
from collections import defaultdict
import time
from datetime import datetime

init()

BENCHMARK_DATA = {
    'start_time': None,
    'end_time': None,
    'processed_urls': defaultdict(int),
    'failed_urls': defaultdict(int),
    'concurrent_requests': 0,
    'max_concurrent': 0
}


# CONFIG
KEYWORDS = ["index", "heroin", "meth"]
#SEARCH_ENGINE = "http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega"
MAX_DEPTH = 4  # DuckDuckGo pages usually don't allow deep crawling

def print_colored(text, color):
    print(color + text + Fore.RESET)

async def fetch_and_extract_links(url, session):
    BENCHMARK_DATA['concurrent_requests'] += 1
    BENCHMARK_DATA['max_concurrent'] = max(
        BENCHMARK_DATA['max_concurrent'],
        BENCHMARK_DATA['concurrent_requests']
    )
    try:
        start = time.monotonic()
        async with session.get(url, timeout=15) as response:
            if response.status != 200:
                print_colored(f"Failed: {url} ({response.status})", Fore.RED)
                return []
            html = await response.text()
            # await add_url_to_mongo(html, str(response.url))  # Optional Mongo analysis
            soup = BeautifulSoup(html, 'html.parser')
            elapsed = time.monotonic() - start
            links = [
                urljoin(str(response.url), a['href'])
                for a in soup.find_all('a', href=True)
                if not a['href'].startswith('mailto:')
            ]
            print_colored(f"[+] Crawled: {url} -> Found {len(links)} links", Fore.GREEN)
            BENCHMARK_DATA['processed_urls'][str(response.url)] = {
                'status': response.status,
                'time': elapsed,
                'links_found': len(links)
            }
            return links
    except Exception as e:
        BENCHMARK_DATA['failed_urls'][url] = str(e)
        print_colored(f"[!] Error: {url} ({e})", Fore.RED)
        return []
    finally:
        BENCHMARK_DATA['concurrent_requests'] -= 1


def print_benchmark_results():
    print("\n=== BENCHMARK RESULTS ===")
    print(f"Total runtime: {BENCHMARK_DATA['end_time'] - BENCHMARK_DATA['start_time']:.2f}s")
    print(f"Total URLs processed: {len(BENCHMARK_DATA['processed_urls'])}")
    print(f"Failed URLs: {len(BENCHMARK_DATA['failed_urls'])}")
    print(f"Max concurrent requests: {BENCHMARK_DATA['max_concurrent']}")
    
    # Calculate average response time
    if BENCHMARK_DATA['processed_urls']:
        avg_time = sum(
            data['time'] for data in BENCHMARK_DATA['processed_urls'].values()
        ) / len(BENCHMARK_DATA['processed_urls'])
        print(f"Avg response time: {avg_time:.2f}s")

async def crawl_recursive(start_url, session, depth=1, max_depth=1):
    if depth > max_depth:
        return
    links = await fetch_and_extract_links(start_url, session)
    tasks = [
        crawl_recursive(link, session, depth + 1, max_depth)
        for link in links
    ]
    await asyncio.gather(*tasks)

async def keyword_crawler(keyword):
    BENCHMARK_DATA['start_time'] = BENCHMARK_DATA['start_time'] or time.monotonic()
    params = {'q': keyword}
    search_url = f"http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Crawler/1.0)"
    }

    connector = ProxyConnector.from_url('socks5://localhost:9050')
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        print_colored(f"[Keyword: {keyword}] Crawling: {search_url}", Fore.CYAN)
        await crawl_recursive(search_url, session, max_depth=MAX_DEPTH)
def run_keyword_crawler(keyword):
    asyncio.run(keyword_crawler(keyword))

def start_multiprocess_crawlers():
    BENCHMARK_DATA['start_time'] = time.monotonic()
    print_colored(f"[+] Starting crawlers for {len(KEYWORDS)} keywords using a process pool...", Fore.YELLOW)
    max_workers = min(len(KEYWORDS), psutil.cpu_count(logical=False))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_keyword_crawler, keyword) for keyword in KEYWORDS]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print_colored(f"[!] Error processing keyword: {e}", Fore.RED)

if __name__ == "__main__":
    start_multiprocess_crawlers()
    print_benchmark_results()
