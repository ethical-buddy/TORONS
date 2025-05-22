import asyncio
import aiohttp
import time
import os
import signal
import threading
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from colorama import Fore, init
from aiohttp_socks import ProxyConnector
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Manager

init(autoreset=True)

# Configuration
KEYWORDS = [
    # Drugs & Substances
    "heroin", "meth", "cocaine", "marijuana", "mdma",
    "lsd", "xanax", "fentanyl", "psychedelics", "prescription",

    # Marketplaces & Finance
    "market", "escrow", "wallet", "bitcoin", "monero",
    "vendor", "shop", "carding", "cc dump", "listing",

    # Indexes & Directories
    "directory", "index", "mirror", "hidden wiki", "onion links",
    "archive", "dump", "pastebin", "leak site", "search",

    # Hacking & Tools
    "exploit", "zero day", "malware", "keylogger", "ransomware",
    "rootkit", "trojan", "phishing", "botnet", "rat",

    # Fraud & Identity
    "identity", "passport", "ssn", "driver license", "forged documents",
    "credit card", "bank login", "paypal", "fake id", "fullz"
]
# Number of threads to spawn per keyword process
THREADS_PER_KEYWORD = 5

# Utility functions

def print_colored(msg, color):
    print(color + msg + Fore.RESET)


def extract_links_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    return [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]

async def fetch_and_extract_links(url, session, benchmark_data, executor):
    try:
        start = time.monotonic()
        async with session.get(url, timeout=15) as resp:
            if resp.status != 200:
                benchmark_data['failed_urls'][url] = f"HTTP {resp.status}"
                print_colored(f"Failed: {url} ({resp.status})", Fore.RED)
                return []

            html = await resp.text()
            loop = asyncio.get_event_loop()
            links = await loop.run_in_executor(executor, lambda: extract_links_from_html(html, str(resp.url)))

            elapsed = time.monotonic() - start
            benchmark_data['processed_urls'][url] = {'status': resp.status, 'time': elapsed, 'links_found': len(links)}
            print_colored(f"[+] Crawled: {url} -> {len(links)} links in {elapsed:.2f}s", Fore.GREEN)
            return links
    except Exception as e:
        benchmark_data['failed_urls'][url] = str(e)
        print_colored(f"[!] Error: {url} ({e})", Fore.RED)
        return []

async def crawl_recursive(url, session, benchmark_data, executor):
    # max_concurrent tracks the highest number of simultaneous recursive calls across all threads
    benchmark_data['current_concurrent'] += 1
    benchmark_data['max_concurrent'] = max(benchmark_data['max_concurrent'], benchmark_data['current_concurrent'])
    try:
        links = await fetch_and_extract_links(url, session, benchmark_data, executor)
        if links:
            await asyncio.gather(*(crawl_recursive(link, session, benchmark_data, executor) for link in links))
    finally:
        benchmark_data['current_concurrent'] -= 1

async def keyword_crawler_async(keyword, benchmark_data):
    search_url = f"http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Crawler/1.0)"}
    connector = ProxyConnector.from_url('socks5://localhost:9050')

    with ThreadPoolExecutor(max_workers=10) as executor:
        async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
            print_colored(f"▶️  [Keyword={keyword}] Start crawling", Fore.CYAN)
            try:
                while True:
                    await crawl_recursive(search_url, session, benchmark_data, executor)
                    await asyncio.sleep(10)
            except asyncio.CancelledError:
                return


def thread_worker(keyword, data_dict):
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(keyword_crawler_async(keyword, data_dict))
    finally:
        loop.close()


def print_clean_results(shared_data):
    # Field definitions:
    #  - max_concurrency: maximum number of simultaneous crawl invocations (async tasks) observed in this keyword process
    #  - thread_count    : number of threads spawned for this keyword
    print_colored("\n===== Clean Crawl Report =====", Fore.MAGENTA)
    for kw, data in shared_data.items():
        proc = data.get('processed_urls', {})
        fail = data.get('failed_urls', {})
        start = data.get('start_time', 0)
        end = data.get('end_time', time.monotonic())
        duration = end - start
        total = len(proc) + len(fail)
        success = len(proc)
        rate = (success / total * 100) if total else 0
        avg_time = (sum(v['time'] for v in proc.values()) / len(proc)) if proc else 0
        max_conc = data.get('max_concurrent', 0)
        threads = data.get('thread_count', 0)

        print_colored(f"\nKeyword: {kw}", Fore.YELLOW)
        print(f"  Duration         : {duration:.2f}s")
        print(f"  URLs crawled     : {success}")
        print(f"  URLs failed      : {len(fail)}")
        print(f"  Success rate     : {rate:.1f}%")
        print(f"  Avg response time: {avg_time:.2f}s")
        print(f"  Max concurrency  : {max_conc}  (max simultaneous async tasks)")
        print(f"  Threads spawned   : {threads}")


def keyword_process(keyword, shared_dict, manager):
    print_colored(f"🔑 Launching process for '{keyword}'", Fore.YELLOW)

    data = manager.dict()
    data['processed_urls'] = manager.dict()
    data['failed_urls'] = manager.dict()
    data['start_time'] = time.monotonic()
    data['end_time'] = None
    data['current_concurrent'] = 0
    data['max_concurrent'] = 0
    # record how many threads were created for this keyword
    data['thread_count'] = THREADS_PER_KEYWORD
    shared_dict[keyword] = data

    threads = []
    for _ in range(THREADS_PER_KEYWORD):
        t = threading.Thread(target=thread_worker, args=(keyword, data), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    data['end_time'] = time.monotonic()


def start_multiprocess_crawlers():
    manager = Manager()
    shared_data = manager.dict()

    processes = [Process(target=keyword_process, args=(kw, shared_data, manager)) for kw in KEYWORDS]
    for p in processes:
        p.start()

    def shutdown(sig, frame):
        print_colored("\n🛑 Terminating crawlers...", Fore.RED)
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
        for data in shared_data.values():
            if data.get('end_time') is None:
                data['end_time'] = time.monotonic()
        print_clean_results(shared_data)
        os._exit(0)

    signal.signal(signal.SIGINT, shutdown)

    for p in processes:
        p.join()
    for data in shared_data.values():
        if data.get('end_time') is None:
            data['end_time'] = time.monotonic()
    print_clean_results(shared_data)

if __name__ == "__main__":
    start_multiprocess_crawlers()
