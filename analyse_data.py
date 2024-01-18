import os
import csv
from bs4 import BeautifulSoup
from nlp import classify_text_batch
from categorize import get_possible_categories

def process_files(directory_path='archive', output_csv_path='data/hateful_files.csv'):
    # Create a CSV file for tracking hateful files
    with open(output_csv_path, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # if directory_path does not exist, create it
        os.makedirs(directory_path, exist_ok=True)
        # Iterate through each file in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith('.csv'):
                continue
            now = csvfile.tell()
            csvfile.seek(0)
            if filename in csvfile.read():
                continue
            csvfile.seek(now)
            file_path = os.path.join(directory_path, filename)

            # Check if the item in the directory is a file
            if os.path.isfile(file_path):
                # Open the file and print its content
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read()

                    # parse the data in html format
                    soup = BeautifulSoup(data, 'html.parser')
                    text_content = soup.text

                    # classify the text
                    classification_result = classify_text_batch([text_content])

                    # Get possible categories for the text
                    categories = get_possible_categories(text_content)

                    # Check if any label is 'HATE'
                    if any(label['label'] == 'HATE' for label in classification_result):
                        # Mark the file as hateful in the CSV file
                        csv_writer.writerow([filename, 'HATEFUL', categories])
                        # print(f'{filename} is marked as HATEFUL.')
                    else:
                        csv_writer.writerow([filename, 'NOT HATEFUL', categories])
                        # print(f'{filename} is marked as NOT HATEFUL.')

if __name__ == "__main__":
    process_files()
