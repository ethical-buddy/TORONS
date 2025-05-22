import asyncio
import aiohttp
import psutil
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import Fore, init
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import concurrent
from multiprocessing import Manager
from collections import defaultdict
from aiohttp_socks import ProxyConnector
import os
import signal
from datetime import datetime
import threading

init()

# Configuration
# KEYWORDS = ["index", "heroin", "meth","porn","marijuana","directory","shop","listing"]
BENCHMARK_DATA = defaultdict(dict)
IGNORE_PATTERNS = ["tel:", "mailto:"]
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

def print_colored(text, color):
    print(color + text + Fore.RESET)

def extract_links_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    return [
        urljoin(base_url, a['href'])
        for a in soup.find_all('a', href=True)
        if not any(p in a['href'] for p in IGNORE_PATTERNS)
    ]

async def fetch_and_extract_links(url, session, benchmark_data, executor):
    try:
        start_time = time.monotonic()
        async with session.get(url, timeout=15) as response:
            if response.status != 200:
                benchmark_data['failed_urls'][url] = f"HTTP {response.status}"
                print_colored(f"Failed: {url} ({response.status})", Fore.RED)
                return []

            html = await response.text()
            loop = asyncio.get_running_loop()
            links = await loop.run_in_executor(
                executor, lambda: extract_links_from_html(html, str(response.url))
            )

            benchmark_data['processed_urls'][url] = {
                'status': response.status,
                'time': time.monotonic() - start_time,
                'links_found': len(links)
            }

            print_colored(f"[+] Crawled: {url} -> Found {len(links)} links", Fore.GREEN)
            return links

    except Exception as e:
        benchmark_data['failed_urls'][url] = str(e)
        print_colored(f"[!] Error: {url} ({e})", Fore.RED)
        return []

async def crawl_recursive(url, session, benchmark_data, executor):
    benchmark_data['current_concurrent'] = benchmark_data.get('current_concurrent', 0) + 1
    benchmark_data['max_concurrent'] = max(
        benchmark_data.get('max_concurrent', 0),
        benchmark_data['current_concurrent']
    )

    try:
        links = await fetch_and_extract_links(url, session, benchmark_data, executor)
        tasks = [
            crawl_recursive(link, session, benchmark_data, executor)
            for link in links
        ]

        if tasks:
            await asyncio.gather(*tasks)

    finally:
        benchmark_data['current_concurrent'] -= 1

async def keyword_crawler(keyword, benchmark_data=None):
    if benchmark_data is None:
        benchmark_data = {
            'processed_urls': {},
            'failed_urls': {},
            'start_time': time.monotonic(),
            'max_concurrent': 0
        }

    search_url = f"http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Crawler/1.0)"}

    connector = ProxyConnector.from_url('socks5://localhost:9050')
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        print_colored(f"[Keyword: {keyword}] Crawling: {search_url}", Fore.CYAN)
        with ThreadPoolExecutor(max_workers=10) as executor:
            try:
                while True:
                    await crawl_recursive(search_url, session, benchmark_data, executor)
                    await asyncio.sleep(10)
            except asyncio.CancelledError:
                pass

    return benchmark_data

def run_keyword_crawler(keyword, shared_data=None):
    benchmark_data = shared_data.setdefault(keyword, Manager().dict()) if shared_data else {}
    try:
        asyncio.run(keyword_crawler(keyword, benchmark_data))
    except KeyboardInterrupt:
        benchmark_data['end_time'] = time.monotonic()
        benchmark_data['thread_count'] = threading.active_count()
        raise

def print_benchmark_results(benchmark_data, file=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = [f"=== Benchmark Report - {timestamp} ===", "=== COMBINED CRAWLER BENCHMARK REPORT ===\n"]

    total_processed = 0
    total_failed = 0
    total_time = 0

    for keyword, data in benchmark_data.items():
        start = data.get('start_time', time.monotonic())
        end = data.get('end_time', time.monotonic())
        duration = end - start
        processed = len(data.get('processed_urls', {}))
        failed = len(data.get('failed_urls', {}))
        total_time += duration
        total_processed += processed
        total_failed += failed
        throughput = processed / duration if duration else 0

        avg_time = (sum(d.get('time', 0) for d in data['processed_urls'].values()) / processed) if processed else 0
        max_conc = data.get('max_concurrent', 0)
        threads = data.get('thread_count', 'N/A')

        output.append(f"[Keyword: {keyword}]\nTime: {duration:.2f}s | URLs: {processed} | Failed: {failed}\nAvg Response Time: {avg_time:.2f}s\nMax Concurrency: {max_conc}\nThreads Used: {threads}\nThroughput: {throughput}\n")

    total_attempts = total_processed + total_failed
    success_rate = (total_processed / total_attempts) * 100 if total_attempts else 0
    output.append(f"[Total Time across all]: {total_time:.2f}s\nTotal URLs Processed: {total_processed}\nTotal Failed: {total_failed}\nOverall Success Rate: {success_rate:.1f}%\n")

    report = "\n".join(output)
    print(report)
    if file:
        with open(file, "w") as f:
            f.write(report)

def start_multiprocess_crawlers():
    print_colored(f"[+] Starting crawlers for {len(KEYWORDS)} keywords...", Fore.YELLOW)
    with Manager() as manager:
        shared_benchmark_data = manager.dict({})

        processes = []
        with ProcessPoolExecutor(max_workers=len(KEYWORDS)) as executor:
            try:
                for keyword in KEYWORDS:
                    shared_benchmark_data[keyword] = manager.dict({
                        'processed_urls': manager.dict(),
                        'failed_urls': manager.dict(),
                        'start_time': time.monotonic(),
                        'max_concurrent': 0
                    })
                    processes.append(executor.submit(run_keyword_crawler, keyword, shared_benchmark_data))

                for p in concurrent.futures.as_completed(processes):
                    p.result()

            except KeyboardInterrupt:
                print_colored("\n[!] KeyboardInterrupt received. Saving benchmark...", Fore.RED)
                for keyword, data in shared_benchmark_data.items():
                    data['end_time'] = time.monotonic()
                    data['thread_count'] = threading.active_count()

                filename = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                print_benchmark_results(dict(shared_benchmark_data), file=filename)
                os._exit(0)

        print_benchmark_results(dict(shared_benchmark_data))

if __name__ == "__main__":
    start_multiprocess_crawlers()

