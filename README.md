# Dark Web Monitoring Tool README (Work in Progress)

## Current Progress

### Problem Statement:
Crawling a robust script that seamlessly integrates Tor and i2p proxies for secure access to the onion network. Utilizing multithreaded partitioning and sophisticated algorithms to extract and analyze data efficiently, the tool aims to provide a secure, streamlined, and comprehensive solution for Dark Web monitoring.

### Solution Approach:

#### 1. Proxy Configuration:
- Utilize Tor and i2p proxies within the script to establish secure connections to the onion network.

#### 2. Multithreaded Partitioning:
- Implement recursive modules running on separate threads, partitioning CPU resources for efficient computation.
- Initial setup includes two partitions: one for accessing the Hidden Wiki and the other for dark web search engines like 'Torch.'

#### 3. Crawling and Machine Learning:
- Recursively crawl data from URLs found on each page.
- Utilize Machine Learning to detect site behaviors and save crucial data to a dedicated database.

#### 4. Dynamic Thread Management:
- Maintain threads until the site is active; upon successful scraping, terminate the thread and initiate new recursions.

#### 5. Targeted Search and Image Analysis:
- Search for custom-made keywords on dark web search engines to locate target URLs.
- Implement deep learning techniques to analyze images found on the dark web, extracting text and interpreting advertisements.

#### 6. Captcha Solving Algorithms:
- Integrate algorithms designed to solve various types of captchas encountered during the crawling process.

### Technical Approach:

#### 1. Proxy Setup:
- Tor, i2p

#### 2. Thread Management:
- Recursive, CPU-partitioned threads

#### 3. Initial Partitions:
- Hidden Wiki, Dark Web Search Engines

#### 4. Data Handling:
- Recursive URL crawling, Machine Learning-based behavior detection

#### 5. Thread Termination:
- Upon successful scraping

#### 6. Search Techniques:
- Custom keyword search, Image analysis with deep learning

#### 7. Captcha Resolution:
- Algorithms to solve diverse captcha challenges

### Software and Technology:

#### 1. Proxy Handling:
- Tor libraries, i2p setup

#### 2. Programming Language:
- Python, Go

#### 3. Multithreading:
- Python's threading module

#### 4. Web Scraping:
- BeautifulSoup, Scrapy, Selenium

#### 5. Machine Learning:
- TensorFlow, Scikit-learn

#### 6. Image Processing:
- OpenCV, TensorFlow for image analysis

#### 7. Captcha Solving:
- Custom algorithms or libraries for captcha resolution

### Team Members & Responsibilities:

- **Suryansh Deshwal:** Cyber Security expert
- **Ayush Agrawal:** Developer
- **Ritik Bhatt:** Developer

## Future Promises

- **Complete Proxy Handling:** Full integration of Tor and i2p proxies for secure and anonymous connections.
- **Optimized Multithreading:** Enhancements to thread management for improved resource utilization and efficiency.
- **Expanded Partitions:** Inclusion of additional partitions for diverse data sources on the Dark Web.
- **Advanced Data Handling:** Incorporation of advanced machine learning algorithms for more accurate behavior detection.
- **Robust Thread Termination:** Improved thread termination strategies for better resource management.
- **Enhanced Search Techniques:** Continued refinement of search techniques, including custom keyword algorithms.
- **Captcha Resolution Optimization:** Ongoing development and improvement of algorithms for solving various captcha challenges.

## Current Work

Recursive web crawler is integrated and data is scraped into a csv database
