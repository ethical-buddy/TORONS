import gzip
import base64
from uuid import uuid4
from datetime import datetime
from bs4 import BeautifulSoup
import motor.motor_asyncio
from nlp import classify_text_batch
from categorize import get_possible_categories
import asyncio
import os

HATEFUL_LABEL = 'HATEFUL'
NOT_HATEFUL_LABEL = 'NOT HATEFUL'

# MongoDB async client
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
collection = client['torons']['pages']

def compress_html(data: str) -> str:
    compressed = gzip.compress(data.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

def sync_nlp_processing(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.text

    classification_result = classify_text_batch([text_content])
    categories = get_possible_categories(text_content)

    label = HATEFUL_LABEL if any(item['label'] == 'HATE' for item in classification_result) else NOT_HATEFUL_LABEL
    return label, categories, compress_html(html)

async def add_url_to_mongo(html: str, url: str = None):
    filename = url or f"{datetime.utcnow().isoformat()}.html"

    # Run CPU-bound NLP stuff in a thread
    label, categories, compressed = await asyncio.to_thread(sync_nlp_processing, html)

    document = {
        "user_id": str(uuid4()),
        "filename": os.path.basename(filename),
        "label": label,
        "categories": ', '.join(categories),
        "compressed_html": compressed,
        "created_at": datetime.utcnow()
    }

    await collection.insert_one(document)
