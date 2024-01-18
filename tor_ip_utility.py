import requests
from stem import Signal, CircStatus, SocketError
from stem.control import Controller
from config import *
from colorama import Fore, Style
from datetime import datetime
import os
import threading
import time
from pathlib import Path


class TorUtility:
    def __init__(self, verbose=True):
        self.is_tor_active = False
        self.tor_enabled = True
        self.lock = threading.Lock()
        self.verbose = verbose
        self.COLOR_RED = f"{Fore.RED}"
        self.COLOR_GREEN = f"{Fore.GREEN}"
        self.COLOR_YELLOW = f"{Fore.YELLOW}"
        self.COLOR_CYAN = f"{Fore.CYAN}"
        self.COLOR_RESET = f"{Style.RESET_ALL}"

        # Initialize history file
        BASE_DIR = Path(__file__).parent
        self.history_file = (BASE_DIR / "data" / "tor_ip_history.txt")
        self.initialize_history_file()

        history_thread = threading.Thread(
            target=self.history_log)
        history_thread.start()

        # Additional attribute to store the current IP
        self.current_ip = None

    def initialize_history_file(self):
        """Initialize the history file."""
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w") as file:
                file.write("Timestamp,IP Address\n")

    def history_log(self):
        """Log current IP address on instance creation"""
        with self.lock:
            self.current_ip = self.get_absolute_current_ip()
            if self.current_ip:
                self.log_ip_change(self.current_ip)
                # if self.verbose:
                #     print(
                #         f"\n\t\t\t\t\t\t{self.COLOR_GREEN}TOR IP: {self.current_ip}{self.COLOR_RESET}")

    def log_ip_change(self, ip_address):
        """Log IP change along with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.history_file, "a") as file:
            file.write(f"{timestamp},{ip_address}\n")

    def get_current_ip(self):
        """Get the current Tor IP address."""
        session = requests.session()
        session.proxies = {'http': 'socks5h://localhost:9050',
                           'https': 'socks5h://localhost:9050'}
        try:
            if self.verbose:
                print(
                    f"\n{self.COLOR_YELLOW}Requesting IP address from Tor...{self.COLOR_RESET}")
            r = session.get('http://httpbin.org/ip')
            r.raise_for_status()
            return r.text
        except requests.exceptions.RequestException as e:
            if self.verbose:
                print(
                    f"\n{self.COLOR_RED}Error during request: {str(e)}{self.COLOR_RESET}")
            return None

    def get_absolute_current_ip(self):
        ip = self.get_current_ip()
        if ip is None:
            return None
        else:
            return ip.split('"')[3]

    def renew_tor_ip(self):
        """Renew the Tor IP address."""
        def renew_circuit(controller):
            try:
                controller.authenticate(password=TOR_PASSWORD)
                if controller.is_newnym_available():
                    controller.signal(Signal.NEWNYM)
                    if self.verbose:
                        print(
                            f"\n{self.COLOR_GREEN}Renewed Tor IP{self.COLOR_RESET}")
                    return True
                else:
                    delay = controller.get_newnym_wait()
                    if self.verbose:
                        print(
                            f"\n{self.COLOR_YELLOW}Delay to create new Tor circuit: {delay}s{self.COLOR_RESET}")
                    return False
            except Exception as e:
                if self.verbose:
                    print(
                        f"\n{self.COLOR_RED}Error renewing Tor IP: {str(e)}{self.COLOR_RESET}")
                return False

        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            renew_circuit(controller)
        history_thread = threading.Thread(
            target=self.history_log)
        history_thread.start()

    def check_tor_circuit_info(self):
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            try:
                controller.authenticate(password=TOR_PASSWORD)
                circuits = controller.get_circuits()
                if not circuits:
                    if self.verbose:
                        print(
                            f"\n{self.COLOR_YELLOW}No Tor circuit established.{self.COLOR_RESET}")
                    return

                if self.verbose:
                    print(
                        f"\n{self.COLOR_GREEN}Current Tor Circuit Information:{self.COLOR_RESET}")

                for circ in circuits:
                    if circ.status == CircStatus.BUILT:
                        print(
                            f"    Circuit ID: {self.COLOR_CYAN}{circ.id}{self.COLOR_RESET}")
                        print(f"    Path for Circuit {circ.id}:")
                        for i, entry in enumerate(circ.path):
                            print(
                                f"{self.COLOR_CYAN}        Node {i + 1}{self.COLOR_RESET}: {entry}")
                        print("\n")
                        print("-" * 10)

            except Exception as e:
                if self.verbose:
                    print(
                        f"\n{self.COLOR_RED}Error checking Tor circuit information: {str(e)}{self.COLOR_RESET}")
        return circuits

    def display_tor_configuration(self):
        try:
            with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
                controller.authenticate(password=TOR_PASSWORD)

                config_parameters = [
                    "Nickname",
                    "BandwidthRate",
                    "BandwidthBurst",
                    "RelayBandwidthRate",
                    "RelayBandwidthBurst",
                    "ExitPolicy",
                    "ContactInfo",
                    "DataDirectory",
                    "ExitRelay",
                    "ExitPolicyRejectPrivate",
                    "HiddenServiceStatistics",
                    "Log",
                    "PublishServerDescriptor",
                    "StrictNodes",
                    "UseBridges",
                    "UseEntryGuards",
                    "UseMicrodescriptors",
                    # Add more configuration parameters as needed
                ]

                # if self.verbose:
                print(
                    f"\n{self.COLOR_GREEN}Tor Configuration Settings:{self.COLOR_RESET}")
                for param in config_parameters:
                    value = controller.get_conf(param)
                    # if self.verbose:
                    print(
                        f"    {self.COLOR_CYAN}{param}:{self.COLOR_RESET} {value}")
        except SocketError as se:
            if self.verbose:
                print(
                    f"\n{self.COLOR_RED}Error connecting to Tor control port: {str(se)}{self.COLOR_RESET}")
        except Exception as e:
            if self.verbose:
                print(
                    f"\n{self.COLOR_RED}Error fetching Tor configuration: {str(e)}{self.COLOR_RESET}")

    def toggle_tor(self, enable):
        """Toggle Tor proxy on or off."""
        self.tor_enabled = enable
        if self.verbose:
            print(
                f"\n{self.COLOR_YELLOW}Tor proxy {'enabled' if enable else 'disabled'}.{self.COLOR_RESET}")
        if not enable and self.verbose:
            print(
                f"\n{self.COLOR_YELLOW}Reverting to direct connection...{self.COLOR_RESET}")

    def view_tor_ip_history(self):
        """View Tor IP history."""
        with open(self.history_file, "r") as file:
            print("\nTor IP History:")
            print(file.read())

    def auto_renew_tor_ip(self):
        """Automatically renew Tor IP address every 10 minutes."""
        print(f"\n{self.COLOR_YELLOW}Starting Auto IP Renewal service [10mins]...{self.COLOR_RESET}")
        while True:
            try:
                if self.verbose:
                    print(
                        f"\n{self.COLOR_YELLOW}Renewing Tor IP address...{self.COLOR_RESET}")
                self.renew_tor_ip()
                self.current_ip = self.get_absolute_current_ip()
                print(
                    f"\n{self.COLOR_GREEN}NEW TOR IP: {self.current_ip}{self.COLOR_RESET}")
                if self.verbose:
                    print(
                        f"\n{self.COLOR_YELLOW}Sleeping for 10 minutes...{self.COLOR_RESET}")
                time.sleep(600)
            except KeyboardInterrupt:
                if self.verbose:
                    print(f"\n{self.COLOR_YELLOW}Exiting...{self.COLOR_RESET}")
                break
            except Exception as e:
                if self.verbose:
                    print(
                        f"\n{self.COLOR_RED}Error: {str(e)}{self.COLOR_RESET}")
                continue

    @staticmethod
    def start_nyx():
        """Start nyx (Tor monitor)."""
        os.system("nyx")

    def run(self):
        while True:
            try:
                if self.verbose:
                    print("\nChoose an option:")
                    print(
                        f"[{self.COLOR_CYAN}1{self.COLOR_RESET}] Get the current Tor IP")
                    print(
                        f"[{self.COLOR_CYAN}2{self.COLOR_RESET}] Renew the Tor IP address")
                    print(
                        f"[{self.COLOR_CYAN}3{self.COLOR_RESET}] Check Tor circuit information")
                    print(
                        f"[{self.COLOR_CYAN}4{self.COLOR_RESET}] Display Tor Configuration Settings")
                    print(
                        f"[{self.COLOR_CYAN}5{self.COLOR_RESET}] Toggle Tor Proxy (Enable/Disable)")
                    print(
                        f"[{self.COLOR_CYAN}6{self.COLOR_RESET}] View Tor IP History")
                    print(
                        f"[{self.COLOR_CYAN}7{self.COLOR_RESET}] Start nyx (Tor monitor)")
                    print(f"[{self.COLOR_CYAN}8{self.COLOR_RESET}] Exit")

                choice = input("Enter the number of your choice: ")
                if choice == "1":
                    current_ip = self.get_absolute_current_ip()
                    print(
                        f"\n{self.COLOR_GREEN}TOR IP: {current_ip}{self.COLOR_RESET}")
                    self.log_ip_change(current_ip)
                elif choice == "2":
                    self.renew_tor_ip()
                elif choice == "3":
                    self.check_tor_circuit_info()
                elif choice == "4":
                    self.display_tor_configuration()
                elif choice == "5":
                    self.toggle_tor(not self.tor_enabled)
                elif choice == "6":
                    self.view_tor_ip_history()
                elif choice == "7":
                    self.start_nyx()
                elif choice == "8":
                    if self.verbose:
                        print(
                            f"\n{self.COLOR_YELLOW}Exiting From Tor Utility...{self.COLOR_RESET}")
                    break
                else:
                    if self.verbose:
                        print(
                            f"\n{self.COLOR_RED}Invalid choice. Please enter a number between 1 and 7.{self.COLOR_RESET}")
            except KeyboardInterrupt:
                if self.verbose:
                    print(f"\n{self.COLOR_YELLOW}Exiting...{self.COLOR_RESET}")
                break
            except Exception as e:
                if self.verbose:
                    print(
                        f"\n{self.COLOR_RED}Error: {str(e)}{self.COLOR_RESET}")
                continue


if __name__ == "__main__":
    # Set verbose to True or False to enable or disable verbose output
    tor_utility = TorUtility(verbose=True)
    tor_utility.run()
