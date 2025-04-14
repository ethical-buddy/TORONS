import os
import gzip
import base64
from bs4 import BeautifulSoup
from nlp import classify_text_batch
from categorize import get_possible_categories
from pymongo import MongoClient
from uuid import uuid4
from datetime import datetime

HATEFUL_LABEL = 'HATEFUL'
NOT_HATEFUL_LABEL = 'NOT HATEFUL'

def create_mongo_client():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['torons']
    collection = db['pages']
    return client, collection

def close_mongo_client(client):
    client.close()

def compress_html(data: str) -> str:
    compressed = gzip.compress(data.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

def insert_data(collection, filename, label, categories, compressed_html):
    categories_str = ', '.join(categories)

    document = {
        'user_id': str(uuid4()),
        'filename': filename,
        'label': label,
        'categories': categories_str,
        'compressed_html': compressed_html,
        'created_at': datetime.utcnow()
    }

    collection.insert_one(document)

def process_file(collection, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        soup = BeautifulSoup(data, 'html.parser')
        text_content = soup.text

        classification_result = classify_text_batch([text_content])
        categories = get_possible_categories(text_content)

        label = HATEFUL_LABEL if any(item['label'] == 'HATE' for item in classification_result) else NOT_HATEFUL_LABEL
        compressed_html = compress_html(data)

        insert_data(collection, os.path.basename(file_path), label, categories, compressed_html)

def process_files(directory_path='archive'):
    os.makedirs(directory_path, exist_ok=True)

    client, collection = create_mongo_client()

    try:
        existing_files = set(doc['filename'] for doc in collection.find({}, {'filename': 1}))

        for filename in os.listdir(directory_path):
            if filename.endswith('.csv') or filename in existing_files:
                continue

            file_path = os.path.join(directory_path, filename)

            if os.path.isfile(file_path):
                process_file(collection, file_path)

    finally:
        close_mongo_client(client)

if __name__ == "__main__":
    process_files()

