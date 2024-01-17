import requests
from tor_ip_utility import TorUtility
import threading
from datetime import datetime


class TorWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.set_tor_proxy()

    def set_tor_proxy(self):
        self.session.proxies = {
            'http': 'socks5h://localhost:9050',
            'https': 'socks5h://localhost:9050'
        }

    def scrape_url(self, url, output_file='output.html'):
        try:
            # Make a request through Tor
            response = self.session.get(url)
            # print("Response from Tor hidden service:", response.text)

            # Save the response to a file
            with open(output_file, 'w') as f:
                f.write(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"+str(response.text))

        except Exception as e:
            print(f"Error: {e}")


def update_ip():
    global ip
    ip = tor_utility.get_absolute_current_ip()


if __name__ == "__main__":
    tor_utility = TorUtility(verbose=False)
    tor_scraper = TorWebScraper()
    autorenew_ip_thread = threading.Thread(
        target=tor_utility.auto_renew_tor_ip)
    autorenew_ip_thread.start()
    # autorenew_ip_thread.join() #This is blocking the main thread
    # Expections: Run update_ip_thread after each time after autorenew_ip_thread is ran, so that ip variable can be updated with the new ip.
    update_ip_thread = threading.Thread(target=update_ip)
    update_ip_thread.start()

    print(tor_utility.get_absolute_current_ip())
    test_url = "http://torch2cjfpa4gwrzsghfd2g6nebckghjkx3bn6xyw6capgj2nqemveqd.onion/"
    while True:
        tor_scraper.scrape_url(url=test_url,
                               output_file='RJPOLICE_HACK_1279_CPC_11/temp/torch.html')
        print(ip)
