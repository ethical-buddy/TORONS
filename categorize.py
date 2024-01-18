import json

def load_categories(file_path='categories.json'):
    with open(file_path, 'r') as json_file:
        categories_data = json.load(json_file)
    return categories_data['categories']

def categorize_text(text, categories):
    result = [category for category, keywords in categories.items() if any(kw.lower() in text.lower() for kw in keywords)]
    return result

def get_possible_categories(text):
    categories = load_categories()
    return categorize_text(text, categories)

if __name__ == "__main__":
    example_text = "This is a sample text about technology and innovation in the marketplace."
    possible_categories = get_possible_categories(example_text)
    print("Possible Categories:", possible_categories)
