# ShadowSight DarkWeb Crawler

## Project Overview
This project is an asynchronous web crawler designed for scraping data from websites on both the Tor (.onion) and I2P (.i2p) networks. Additionally, it includes an NLP component for hate speech classification on the extracted text data.

## Features
- **Asynchronous Web Crawling:**
  - Concurrent crawling of Tor and I2P websites using asyncio and aiohttp.
  - Data is saved to HTML files in the "archive" directory.
  - CSV file (data.csv) stores URLs and timestamps for tracking purposes.
  - Temporary URLs are stored in a database (temp/scraped.txt) to avoid redundant crawling.

- **Randomization and Security:**
  - Random user agents enhance anonymity during crawling.
  - Secure random strings for various purposes.

- **NLP Analysis:**
  - Hate speech classification using a pre-trained model (Hate-speech-CNERG/dehatebert-mono-english).
  - Analysis of text data extracted during web crawling.

- **User Interface:**
  - Command-Line Interface (CLI) (main.py) for interactive menu-based control.
  - Options to initiate web crawling through Tor, I2P, or both.
  - Tor IP Utility for checking the current IP address.
  
- **Continuous Background Processing:**
  - Background thread (run_process_files_continuously) for continuous file processing.

## Prerequisites
- Python 3.x
- Install required packages using: `pip install -r requirements.txt`
- Ensure Tor is running and configured for web crawling through the Tor network.

## Usage
1. Run `main.py` to access the CLI menu and start web crawling or run the Tor IP Utility.
2. Execute `async_crawl4.py` and `async_crawl_i2p.py` independently for specific networks.
3. Continuous file processing is handled in the background.

## File Structure
- `async_crawl4.py`: Asynchronous web crawler for Tor network.
- `async_crawl_i2p.py`: Asynchronous web crawler for I2P network.
- `main.py`: CLI for user interaction and control.
- `nlp_main.py`: NLP script for hate speech classification.
- `requirements.txt`: List of required Python packages.
- `temp/`: Folder for temporary data storage.
- `archive/`: Folder for storing scraped data.

## Command Line Interface
![Command Line Interface](https://github.com/TORONS/RJPOLICE_HACK_1279_CPC_11/blob/main/CLI_Interface.png)

## Acknowledgements
- This project uses the transformers library by Hugging Face for NLP tasks.
- The hate speech classification model used is Hate-speech-CNERG/dehatebert-mono-english.

## Contributors
- **Suryansh Deshwal:** Cyber Security expert
- **Ayush Agrawal:** Developer
- **Ritik Bhatt:** Developer



