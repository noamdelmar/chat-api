import logging
from websocket import WebSocket
import json

logging.basicConfig(filename='chat_server.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class FileServer:
    def __init__(self, chat_server):
        self.rooms = chat_server.rooms
        self.chat_server = chat_server

    def handle_file(self, data, room, sender_socket, rooms, remove_client):
        file_info = data.get('file')
        if file_info:
            file_name = file_info.get('name')
            file_content = file_info.get('content')
            username = file_info.get('username')
            message = file_info.get('message')

            # Broadcast the file to other clients in the room
            self.broadcast_file(file_name, file_content, username,message, sender_socket, room, rooms, remove_client)


    def broadcast_file(self, file_name, file_content,username,message, sender_socket, room, rooms, remove_client):
        try:
            # Prepare the file message to be broadcasted
            file_data = {
                'type': 'file',
                'file': {
                    'name': file_name,
                    'content': file_content,
                    'username': username,
                    'message': message
                }
            }
            json_message = json.dumps(file_data)

            # Broadcast the file message to other clients in the room
            if room in rooms:
                room_clients = rooms[room]
                for _, client_socket in room_clients:
                    if client_socket != sender_socket:
                        try:
                            WebSocket.send_message(client_socket, json_message, 'file')
                        except Exception as e:
                            print(f"Error broadcasting file: {e}")
                            remove_client(_, room, client_socket)

        except Exception as e:
            print(f"Error preparing file data: {e}")


