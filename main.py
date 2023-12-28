#Importing the required modules
import requests
from bs4 import BeautifulSoup
import threading
import csv
import time
from random import choice
import spacy
import signal
import os
import time
from tor_ip_utility import renew_tor_ip


# Import spaCy and load the English model
nlp = spacy.load("en_core_web_sm")

# Global variables
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
]
MAX_RETRIES = 3
BACKOFF_FACTOR = 2
DATABASE_REFRESH_INTERVAL = 600  # 10 minutes in seconds

# Create a CSV file to store the scraped data
time_now = int(time.time())
csv_file_path = f'web_scraper_keywords-{time_now}.csv'
csv_header = ['url', 'found_keyword', 'all_keywords']

# Use a text file as a temporary database for scraped URLs
temp_db_file_path = 'scraped_urls.txt'

# Global variable for the thread counter
thread_counter = 0
thread_counter_lock = threading.Lock()

# Flag to indicate if the program should stop
stop_program = False

# Signal handler function
def handle_interrupt(signum, frame):
    global stop_program
    print("\nCtrl + C pressed. Stopping the program...")
    stop_program = True

# Register the signal handler for Ctrl + C
signal.signal(signal.SIGINT, handle_interrupt)

# Function to increment the thread counter
def increment_thread_counter():
    global thread_counter
    with thread_counter_lock:
        thread_counter += 1

# Function to decrement the thread counter
def decrement_thread_counter():
    global thread_counter
    with thread_counter_lock:
        thread_counter -= 1

# Function to get the current thread count
def get_thread_count():
    with thread_counter_lock:
        return thread_counter

# Function to initialize the CSV file with headers
def initialize_csv():
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_header)

# Function to write data to the CSV file
def write_to_csv(data):
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

# Function to read scraped URLs from the text file
def read_scraped_urls():
    if os.path.exists(temp_db_file_path):
        with open(temp_db_file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file.readlines())
    return set()

# Function to write scraped URLs to the text file
def write_scraped_urls(urls):
    with open(temp_db_file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(urls))

# Function to extract important keywords and nouns from text
def extract_keywords_and_nouns(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop and token.pos_ != 'DET']
    nouns = [token.text for token in doc if token.is_alpha and not token.is_stop and token.pos_ == 'NOUN']
    return keywords, nouns

# Function to scrape a webpage, find links, and run the same function for each link
def scrape_url(url, keywords_to_find, retries=MAX_RETRIES):
    global stop_program, thread_counter  # Access the global stop_program and thread_counter variables

    try:
        # Check if the program should stop
        if stop_program:
            return

        # Increment the thread counter
        increment_thread_counter()

        # Read scraped URLs from the text file
        scraped_urls = read_scraped_urls()

        # Check if the URL has already been scraped
        if url in scraped_urls:
            return

        # Set User-Agent header
        USER_AGENT = choice(USER_AGENTS)
        headers = {'User-Agent': USER_AGENT}

        # Make an HTTP request to the URL with retries and backoff
        with requests.get(url, headers=headers) as response:
            response.raise_for_status()

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract important keywords and nouns from the page content
            page_text = soup.get_text().lower()
            all_keywords, nouns = extract_keywords_and_nouns(page_text)

            # Check if any of the keywords_to_find is present in the page content
            found_keywords = [keyword for keyword in keywords_to_find if keyword in all_keywords]

            if found_keywords:
                # Store the data in the CSV file
                write_to_csv([url, ', '.join(found_keywords), ', '.join(all_keywords)])

            # Add the URL to the set of scraped URLs
            scraped_urls.add(url)

            # Write scraped URLs back to the text file
            write_scraped_urls(scraped_urls)

            # Find all links on the page
            links = [a['href'] for a in soup.find_all('a', href=True)]

            # Run the same function for each link in a separate thread
            threads = []
            for link in links:
                full_url = link if link.startswith('http') else f'{url}/{link}'
                thread = threading.Thread(target=scrape_url, args=(full_url, keywords_to_find))
                threads.append(thread)
                thread.start()


        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Decrement the thread counter
        decrement_thread_counter()

    except requests.RequestException as e:
        print(f"Error while scraping {url}: {e}")

        if retries > 0:
            # Implement a backoff strategy
            backoff_time = (MAX_RETRIES - retries + 1) * BACKOFF_FACTOR
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)

            # Retry the request
            scrape_url(url, keywords_to_find, retries - 1)

        decrement_thread_counter()  # Decrement the counter on error

# Function to refresh the database periodically
def refresh_database():
    while True:
        time.sleep(DATABASE_REFRESH_INTERVAL)
        # Print the current thread count
        print(f"Current thread count: {get_thread_count()}")
        # Clear the text file content for the temporary database
        open(temp_db_file_path, 'w').close()
        print("Database refreshed.")

# Example usage
if __name__ == "__main__":
    # start_url = 'https://en.wikipedia.org/wiki/Tesla,_Inc.'
    # keywords_to_find = ['cars', 'ant', 'insect']
    start_url = 'https://www.hackthebox.com/'
    keywords_to_find = ['hacking', 'linux', 'shell']

    # Initialize the CSV file with headers
    initialize_csv()

    # Start a thread to refresh the database periodically
    refresh_thread = threading.Thread(target=refresh_database)
    refresh_thread.start()

    try:
        # Start scraping
        scrape_url(start_url, keywords_to_find)

        # Wait for the refresh thread to finish
        refresh_thread.join()

    except KeyboardInterrupt:
        # Handle Ctrl + C
        print("\nCtrl + C pressed. Stopping the program...")

    finally:
        # Clean up (if needed)
        pass
