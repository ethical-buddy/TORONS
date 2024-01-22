import os
from bs4 import BeautifulSoup
from nlp import classify_text_batch
from categorize import get_possible_categories
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime

HATEFUL_LABEL = 'HATEFUL'
NOT_HATEFUL_LABEL = 'NOT HATEFUL'

def create_session():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect('employee')
    return cluster, session

def close_session(cluster):
    cluster.shutdown()

def insert_data(session, filename, label, categories):
    # Convert categories list to a string
    categories_str = ', '.join(categories)

    insert_query = """
        INSERT INTO lol (user_id, filename, label, categories) VALUES (
            UUID(), %s, %s, %s
        );
    """
    session.execute(insert_query, (filename, label, categories_str))

def process_file(session, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        soup = BeautifulSoup(data, 'html.parser')
        text_content = soup.text

        classification_result = classify_text_batch([text_content])
        categories = get_possible_categories(text_content)

        label = HATEFUL_LABEL if any(label['label'] == 'HATE' for label in classification_result) else NOT_HATEFUL_LABEL

        insert_data(session, file_path, label, categories)

def process_files(directory_path='archive'):
    os.makedirs(directory_path, exist_ok=True)

    cluster, session = create_session()

    try:
        session.execute("SELECT filename FROM lol")  # Test connection
    except Exception as e:
        print(f"Error connecting to Cassandra: {e}")
        return
    else:
        for filename in os.listdir(directory_path):
            if filename.endswith('.csv'):
                continue

            now = session.execute("SELECT filename FROM lol").current_rows
            if filename in now:
                continue

            file_path = os.path.join(directory_path, filename)

            if os.path.isfile(file_path):
                process_file(session, file_path)

    finally:
        close_session(cluster)

if __name__ == "__main__":
    process_files()




