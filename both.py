import asyncio
from colorama import Fore, Style
from async_crawl4 import main as tor_main
from async_crawl_i2p import main as i2p_main

async def crawl_both():
    tasks = [tor_main(), i2p_main()]
    await asyncio.gather(*tasks)

def main():
    print(f"\n{Fore.YELLOW}Starting web crawling through both Tor and I2P...{Style.RESET_ALL}")
    asyncio.run(crawl_both())

if __name__ == "__main__":
    main()
