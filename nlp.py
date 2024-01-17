import os
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

def classify_text_batch(input_texts):
    model_name = "Hate-speech-CNERG/dehatebert-mono-english"
    saved_model_path = "./nlp/saved_model"

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
        model = AutoModelForSequenceClassification.from_pretrained(saved_model_path)

    # Using the high-level pipeline
    pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)

    results = []
    for input_text in input_texts:
        # Split the input text into chunks of 512 characters
        chunks = [input_text[i:i + 512] for i in range(0, len(input_text), 512)]
        for chunk in chunks:
            result_pipeline = pipe(chunk)
            results.append({'label': result_pipeline[0]['label'], 'score': result_pipeline[0]['score']})

    return results

if __name__ == "__main__":
    text_to_classify = "I like you. I love you."
    results = classify_text_batch([text_to_classify])
    print(results)
