import csv
import os
from bs4 import BeautifulSoup
from nlp import classify_text_batch
from categorize import get_possible_categories

HATEFUL_LABEL = 'HATEFUL'
NOT_HATEFUL_LABEL = 'NOT HATEFUL'

def process_file(file_path, csv_writer):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        soup = BeautifulSoup(data, 'html.parser')
        text_content = soup.text

        classification_result = classify_text_batch([text_content])
        categories = get_possible_categories(text_content)

        if any(label['label'] == 'HATE' for label in classification_result):
            csv_writer.writerow([file_path, HATEFUL_LABEL, categories])
        else:
            csv_writer.writerow([file_path, NOT_HATEFUL_LABEL, categories])

def process_files(directory_path='archive', output_csv_path='data/hateful_files.csv'):
    with open(output_csv_path, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        os.makedirs(directory_path, exist_ok=True)

        for filename in os.listdir(directory_path):
            if filename.endswith('.csv'):
                continue

            now = csvfile.tell()
            csvfile.seek(0)
            if filename in csvfile.read():
                continue
            csvfile.seek(now)

            file_path = os.path.join(directory_path, filename)

            if os.path.isfile(file_path):
                process_file(file_path, csv_writer)

if __name__ == "__main__":
    process_files()