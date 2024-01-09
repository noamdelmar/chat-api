# app.py
from flask import Flask, jsonify
from flask_socketio import SocketIO
from chat_server import ChatServer
import threading
from flask_cors import CORS

PORT = 8080

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
server = ChatServer(PORT)

@app.route('/get_usernames', methods=['GET'])
def get_usernames():
    usernames = server.get_usernames()
    return jsonify({'usernames': usernames})

if __name__ == "__main__":
    socketio.start_background_task(server.start)  # Use SocketIO's background task instead of threading.Thread
    socketio.run(app, port=PORT, debug=True)  # Enable debug mode for better error reporting during development
