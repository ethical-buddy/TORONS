import asyncio
from colorama import Fore, Style
import threading

# Import the main functions from the crawlers
from async_crawl4 import start_crawlers as tor_main
from async_crawl_i2p import main as i2p_main

# Runs the periodic retry task in a thread
# def run_periodic_retry_scrape():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(periodic_retry_scrape())

# Main entry point
if __name__ == '__main__':
    # Start the periodic retry thread (background)
    # retry_thread = threading.Thread(target=run_periodic_retry_scrape)
    # retry_thread.daemon = True
    # retry_thread.start()

    # Start Tor-based crawler (multi-core handled inside)
    print(f"\n{Fore.YELLOW}Starting web crawling through Tor...{Style.RESET_ALL}")
    tor_main()

    # Start I2P-based crawler (single-threaded async)
    # print(f"\n{Fore.MAGENTA}Starting web crawling through I2P...{Style.RESET_ALL}")
    # asyncio.run(i2p_main())

