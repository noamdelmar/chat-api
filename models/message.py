import logging
from websocket import WebSocket
logging.basicConfig(filename='chat_server.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class MessageServer:
    def __init__(self, chat_server):
        self.rooms = chat_server.rooms
        self.chat_server = chat_server

    def broadcast_message(self, message, sender_socket, room, rooms, remove_client):
        if room in rooms:
            room_clients = rooms[room]
            for _, client_socket in room_clients:
                if client_socket != sender_socket:
                    try:
                        WebSocket.send_message(client_socket, message)
                    except:
                        remove_client(_, room, client_socket)