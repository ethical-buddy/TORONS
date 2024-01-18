import asyncio
from colorama import Fore, Style
from async_crawl4 import main as tor_main
from async_crawl_i2p import main as i2p_main
from async_crawl4 import clear_temp_db_data, periodic_retry_scrape
import threading

def run_periodic_retry_scrape():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(periodic_retry_scrape())

print(f"\n{Fore.YELLOW}Starting web crawling through Tor...{Style.RESET_ALL}")


retry_thread = threading.Thread(target=run_periodic_retry_scrape)
retry_thread.daemon = True
retry_thread.start()

clear_thread = threading.Thread(target=clear_temp_db_data)
clear_thread.daemon = True  # The thread will exit when the main program exits
clear_thread.start()
asyncio.run(tor_main())
