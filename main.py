# main.py
from app import app, socketio
PORT = 5050

if __name__ == "__main__":
    socketio.run(app, port=PORT, debug=False)

