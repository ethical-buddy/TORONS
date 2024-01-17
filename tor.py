import asyncio
from colorama import Fore, Style
from async_crawl4 import main as tor_main
from async_crawl_i2p import main as i2p_main


print(f"\n{Fore.YELLOW}Starting web crawling through Tor...{Style.RESET_ALL}")
asyncio.run(tor_main())
