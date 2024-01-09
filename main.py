import os
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
from chat_server import ChatServer
from routes import routes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

PORT = int(os.environ.get('PORT', 5050))

server = ChatServer(PORT)
app.register_blueprint(routes)

if __name__ == "__main__":
    threading.Thread(target=server.start).start()
    socketio.run(app)