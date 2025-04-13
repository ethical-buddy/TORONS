from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from pymongo import MongoClient
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def create_mongo_client():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['employee']
    collection = db['lol']
    return client, collection

def close_mongo_client(client):
    client.close()

def read_data_from_mongo():
    client, collection = create_mongo_client()
    try:
        docs = collection.find({}, {'_id': 0, 'filename': 1, 'label': 1, 'categories': 1})
        data = [(doc['filename'], doc['label'], doc['categories']) for doc in docs]
        return data
    finally:
        close_mongo_client(client)

@app.route('/')
def index():
    data = read_data_from_mongo()
    return render_template('index.html', data=data)

@socketio.on('update_data')
def handle_update_data():
    def background_thread():
        while True:
            time.sleep(5)  # Adjust the sleep duration as needed
            data = read_data_from_mongo()
            socketio.emit('data_updated', {'data': data})
    threading.Thread(target=background_thread).start()

@app.route('/archive/<filename>')
def view_file(filename):
    # Assuming the HTML files are in the 'archive' directory
    return send_from_directory('../archive', filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)

