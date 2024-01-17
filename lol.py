import asyncio
from colorama import Fore, Style
from async_crawl4 import main as async_main

def display_menu():
    print("\nChoose an option:")
    print(f"[{Fore.CYAN}1{Style.RESET_ALL}] Start web crawling")
    print(f"[{Fore.CYAN}2{Style.RESET_ALL}] Exit")

def main():
    print(f"{Fore.GREEN}Welcome to the Async Web Crawler CLI!{Style.RESET_ALL}")

    while True:
        try:
            display_menu()
            choice = input("Enter the number of your choice: ")

            if choice == "1":
                print(f"\n{Fore.YELLOW}Starting web crawling...{Style.RESET_ALL}")
                asyncio.run(async_main())
            elif choice == "2":
                print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please enter a number between 1 and 2.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
