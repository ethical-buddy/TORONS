import asyncio
from colorama import Fore, Style
from async_crawl4 import start_multiprocess_crawlers as tor_main
from async_crawl_i2p import main as i2p_main
import os
import sys
from pathlib import Path
from tor_ip_utility import TorUtility
# from analyse_data_mongo import process_files
import time
import threading
from pyfiglet import Figlet
import platform
import warnings
import subprocess
import cProfile

warnings.filterwarnings("ignore")


def print_banner():
    custom_fig = Figlet(font='slant')  # You can choose a different font
    banner_text = custom_fig.renderText('T_O_R_O_N_S ')
    print(f"{Fore.RED}{banner_text}{Style.RESET_ALL}")


def display_system_info():
    print(f"\n{Fore.CYAN}System Information:{Style.RESET_ALL}")
    print(f"  OS: {platform.system()} ")
    print(f"  Processor: {platform.processor()}")
    print(f"  Python Version: {platform.python_version()}")
    print(f"  Architecture: {platform.architecture()}")


def run_process_files_continuously():
    while True:
        # process_files()
        time.sleep(60)


BASE_URL = Path(__file__).parent
tor_file = str(BASE_URL / "tor.py")
i2p_file = str(BASE_URL / "i2p.py")
both_file = str(BASE_URL / "both.py")
tor_ip_utility_file = str(BASE_URL / "tor_ip_utility.py")


def open_new_terminal(command):
    if sys.platform == "win32":
        os.system(f'start cmd /k "{command}"')
    elif sys.platform.startswith("linux"):
        # Try using gnome-terminal, then xterm, then fallback
        if os.system("which gnome-terminal > /dev/null 2>&1") == 0:
             os.system(f'gnome-terminal -- bash -c \'{command}; exec bash\'')
        elif os.system("which xterm > /dev/null 2>&1") == 0:
             os.system(f'xterm -hold -e "{command}"')
        else:
             os.system(f'{os.getenv("TERM")} -e {command}')
    elif sys.platform == "darwin":  
        os.system(f'open -a Terminal.app {command}')
    else:
        NotImplementedError(f"Unsupported Operating System: {sys.platform}")

async def crawl_both():
    tasks = [tor_main(), i2p_main()]
    await asyncio.gather(*tasks)

def display_realtime_resource_usage():
    import psutil
    print(f"\n{Fore.CYAN}Entering dynamic resource usage mode.{Style.RESET_ALL}")
    print("Press Ctrl+C to return to the main menu.\n")
    try:
        while True:
            cpu_percents = psutil.cpu_percent(interval=1, percpu=True)
            memory = psutil.virtual_memory()
            usage_str = " | ".join(f"Core {i}: {p}%" for i, p in enumerate(cpu_percents))
            mem_str = f"Memory usage: {memory.percent}% of {round(memory.total/1e9,1)}GB total"
            # Use carriage return to overwrite the same line and then print the memory usage on a new line.
            # Alternatively, clear the screen if you want a full refresh (using os.system("clear") or similar)
            print(f"\r{usage_str}  ||  {mem_str}", end="", flush=True)
    except KeyboardInterrupt:
        # When the user interrupts (Ctrl+C), add a newline and exit the view.
        print(f"\n{Fore.YELLOW}Exiting dynamic resource usage view...{Style.RESET_ALL}")

def display_menu():
    print("\nChoose an option:")
    print(
        f"  {Fore.CYAN}[{Style.RESET_ALL}1{Fore.CYAN}]{Style.RESET_ALL} Start web crawling through Tor")
    print(
        f"  {Fore.CYAN}[{Style.RESET_ALL}2{Fore.CYAN}]{Style.RESET_ALL} Start web crawling through I2P")
    print(
        f"  {Fore.CYAN}[{Style.RESET_ALL}3{Fore.CYAN}]{Style.RESET_ALL} Start web crawling through both Tor and I2P")
    print(
        f"  {Fore.CYAN}[{Style.RESET_ALL}4{Fore.CYAN}]{Style.RESET_ALL} Run Tor IP Utility")
    print(
        f"  {Fore.CYAN}[{Style.RESET_ALL}5{Fore.CYAN}]{Style.RESET_ALL} Exit")

    print(f"  {Fore.CYAN}[{Style.RESET_ALL}5{Fore.CYAN}]{Style.RESET_ALL} Exit")

    print(f"  {Fore.CYAN}[{Style.RESET_ALL}6{Fore.CYAN}]{Style.RESET_ALL} Show system resource usage")


def main():
    print_banner()
    display_system_info()

    while True:
        try:
            display_menu()
            choice = input("Enter the number of your choice: ")

            if choice == "1":
                print(
                    f"\n{Fore.YELLOW}Starting web crawling through Tor...{Style.RESET_ALL}")
                command = f"{sys.executable} {tor_file}"
                # subprocess.Popen([sys.executable, tor_file])
                open_new_terminal(command)
            elif choice == "2":
                print(
                    f"\n{Fore.YELLOW}Starting web crawling through I2P...{Style.RESET_ALL}")
                command = f"{sys.executable} {i2p_file}"
                open_new_terminal(command)
            elif choice == "3":
                print(
                    f"\n{Fore.YELLOW}Starting web crawling through both Tor and I2P...{Style.RESET_ALL}")
                command = f"{sys.executable} {both_file}"
                open_new_terminal(command)
            elif choice == "4":
                print(
                    f"\n{Fore.YELLOW}Running Tor IP Utility...{Style.RESET_ALL}")
                tor_ip_utility = TorUtility(verbose=True)
                tor_ip_utility.run()
            elif choice == "5":
                print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                sys.exit(0)
            elif choice == "6":
                display_realtime_resource_usage()
            else:
                print(
                    f"\n{Fore.RED}Invalid choice. Please enter a number between 1 and 5.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    process_files_thread = threading.Thread(
        target=run_process_files_continuously, daemon=True)
    process_files_thread.start()
    tor_utility_instance = TorUtility(False)
    auto_renew_ip_thread = threading.Thread(
        target=tor_utility_instance.auto_renew_tor_ip, daemon=True)
    auto_renew_ip_thread.start()
    # profiler = cProfile.Profile()

    # Start profiling
    # profiler.enable()

    # Run the code you want to profile
    # your_function_to_profile()
    main()
    # Stop profiling
    # profiler.disable()

    # Save results to file
    # profiler.dump_stats('profile_output.prof')
