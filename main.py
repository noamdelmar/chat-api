import os
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS
import threading
from chat_server import ChatServer
from routes import routes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)  # Enable CORS for all routes

PORT = int(os.environ.get('PORT', 8080))

server = ChatServer(PORT)
app.register_blueprint(routes)

if __name__ == "__main__":
    threading.Thread(target=server.start).start()
    socketio.run(app)
