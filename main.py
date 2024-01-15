import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS  
import threading
from chat_server import ChatServer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app) 

PORT = int(os.environ.get('PORT', 8080))

server = ChatServer(PORT)

if __name__ == "__main__":
    threading.Thread(target=server.start).start()
    socketio.run(app)
