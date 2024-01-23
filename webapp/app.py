from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def create_session():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect('employee')
    return cluster, session

def close_session(cluster):
    cluster.shutdown()

def read_data_from_cassandra():
    cluster, session = create_session()
    try:
        result_set = session.execute("SELECT filename, label, categories FROM lol")
        data = [(row.filename, row.label, row.categories) for row in result_set]
        return data
    finally:
        close_session(cluster)

@app.route('/')
def index():
    data = read_data_from_cassandra()
    return render_template('index.html', data=data)

@socketio.on('update_data')
def update_data():
    while True:
        time.sleep(5)  # Adjust the sleep duration as needed
        data = read_data_from_cassandra()
        socketio.emit('data_updated', {'data': data})

@app.route('/archive/<filename>')
def view_file(filename):
    # Assuming the HTML files are in the 'archive' directory
    return send_from_directory('../archive', filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)



