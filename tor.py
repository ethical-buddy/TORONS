import asyncio
import psutil
from colorama import Fore, Style
from async_crawl4 import start_multiprocess_crawlers
# from async_crawl4 import clear_temp_db_data  # if using temp DB (optional)
import threading

print(f"{Fore.CYAN}Available physical cores: {psutil.cpu_count(logical=False)}{Style.RESET_ALL}")
print(f"\n{Fore.YELLOW}Starting surface web crawling via DuckDuckGo...{Style.RESET_ALL}")

# Optional: Clear temp DB in a background thread if you're still logging scraped URLs
# clear_thread = threading.Thread(target=clear_temp_db_data)
# clear_thread.daemon = True
# clear_thread.start()

# Start the surface web crawler (multiprocess per keyword)
start_multiprocess_crawlers()

