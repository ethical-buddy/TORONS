import os
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path
model_name = "Hate-speech-CNERG/dehatebert-mono-english"
BASE_DIR = Path(__file__).resolve().parent
saved_model_path = (BASE_DIR / "./saved_model")

# Check if the model is already saved
if not os.path.exists(saved_model_path):
    print("Downloading and saving the model...")
    # Save model to the specified path
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer.save_pretrained(saved_model_path)
    model.save_pretrained(saved_model_path)
else:
    # Load model from the saved path
    tokenizer = AutoTokenizer.from_pretrained(saved_model_path)
    model = AutoModelForSequenceClassification.from_pretrained(
        saved_model_path)

# Using the high-level pipeline
pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Example text for classification
text_to_classify = "I like you. I love you."

# Using the high-level pipeline
result_pipeline = pipe(text_to_classify)
print("Using pipeline:")
print("Label:", result_pipeline[0]['label'])
print("Score:", result_pipeline[0]['score'])
