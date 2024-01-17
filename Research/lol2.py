import asyncio
from colorama import Fore, Style
from async_crawl4 import main as tor_main
from async_crawl_i2p import main as i2p_main
import os
import subprocess
import sys
from pathlib import Path
from tor_ip_utility import TorUtility

BASE_URL = Path(__file__).parent
tor_file = str(BASE_URL / "tor.py")
i2p_file = str(BASE_URL / "i2p.py")
both_file = str(BASE_URL / "both.py")
tor_ip_utility_file = str(BASE_URL / "tor_ip_utility.py")


def open_new_terminal(command):
    os.system(f'start cmd /k "{command}"')


async def crawl_both():
    tasks = [tor_main(), i2p_main()]
    await asyncio.gather(*tasks)


def display_menu():
    print("\nChoose an option:")
    print(f"[{Fore.CYAN}1{Style.RESET_ALL}] Start web crawling through Tor")
    print(f"[{Fore.CYAN}2{Style.RESET_ALL}] Start web crawling through I2P")
    print(
        f"[{Fore.CYAN}3{Style.RESET_ALL}] Start web crawling through both Tor and I2P")
    print(f"[{Fore.CYAN}4{Style.RESET_ALL}] Run Tor IP Utility")
    print(f"[{Fore.CYAN}5{Style.RESET_ALL}] Exit")


def main():
    print(f"{Fore.GREEN}Welcome to the Async Web Crawler CLI!{Style.RESET_ALL}")

    while True:
        try:
            display_menu()
            choice = input("Enter the number of your choice: ")

            if choice == "1":
                print(f"\n{Fore.YELLOW}Starting web crawling through Tor...{Style.RESET_ALL}")
                # asyncio.run(tor_main())
                command = f"{sys.executable} {tor_file}"
                open_new_terminal(command)
            elif choice == "2":
                print(f"\n{Fore.YELLOW}Starting web crawling through I2P...{Style.RESET_ALL}")
                command = f"{sys.executable} {i2p_file}"
                open_new_terminal(command)
            elif choice == "3":
                print(f"\n{Fore.YELLOW}Starting web crawling through both Tor and I2P...{Style.RESET_ALL}")
                command = f"{sys.executable} {both_file}"
                open_new_terminal(command)
            elif choice == "4":
                print(f"\n{Fore.YELLOW}Running Tor IP Utility...{Style.RESET_ALL}")
                tor_ip_utility = TorUtility(verbose=True)
                tor_ip_utility.run()
            elif choice == "5":
                print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please enter a number between 1 and 5.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

