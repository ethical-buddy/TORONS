from flask import Flask, render_template, send_from_directory
import os
import csv

app = Flask(__name__)

def read_csv(file_path):
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(list(row.values()))
    return data

@app.route('/')
def index():
    file_path = 'data/hateful_files.csv'  # Update with your actual CSV file path
    data = read_csv(file_path)
    return render_template('index.html', data=data)

@app.route('/archive/<filename>')
def view_file(filename):
    # Assuming the HTML files are in the 'archive' directory
    return send_from_directory('../archive', filename)

if __name__ == '__main__':
    app.run(debug=True)
