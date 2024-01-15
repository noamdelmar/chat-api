import logging
from websocket import WebSocket
import json

logging.basicConfig(filename='chat_server.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class AudioServer: 
    def __init__(self, chat_server):
        self.rooms = chat_server.rooms
        self.chat_server = chat_server

    def handle_audio(self, audio_content, username, room, sender_socket, rooms, remove_client):
        try:
            audio = audio_content.get('content')

            self.broadcast_audio(audio,username,room, sender_socket, rooms, remove_client)

        except Exception as e:
            print(f"Error preparing audio data: {e}")


    def get_audio_data(self, client_socket):
        try:
            frame = client_socket.recv(2048)

            payload_length = frame[1] & 127
            mask_start = 2

            if payload_length == 126:
                payload_length = int.from_bytes(frame[2:4], byteorder='big')
                mask_start = 4
            elif payload_length == 127:
                payload_length = int.from_bytes(frame[2:10], byteorder='big')
                mask_start = 10

            mask = frame[mask_start:mask_start + 4]
            data_start = mask_start + 4

            payload = bytearray()
            for i in range(payload_length):
                payload.append(frame[data_start + i] ^ mask[i % 4])

            return bytes(payload)  # Return raw bytes

        except (ConnectionResetError, ValueError, Exception) as e:
            logging.error(f"Error in get_audio_data: {e}")
            return None

    def receive_audio(self, client_socket):
        try:
            opcode = client_socket.recv(1)
            if not opcode:
                return None

            payload_length = ord(client_socket.recv(1)) & 127

            if payload_length == 126:
                payload_length = int.from_bytes(client_socket.recv(2), byteorder='big')
            elif payload_length == 127:
                payload_length = int.from_bytes(client_socket.recv(8), byteorder='big')

            mask = client_socket.recv(4)
            payload = bytearray()

            for i in range(payload_length):
                payload.append(client_socket.recv(1)[0] ^ mask[i % 4])

            return bytes(payload)

        except (ConnectionResetError, ValueError) as e:
            logging.error(f"Error in receive_audio: {e}")
            return None
        
    def broadcast_audio(self, audio, username,room, sender_socket, rooms, remove_client):
        try:
            audio_data = {
                'type': 'audio',
                'audio': {
                    'content': audio,
                    'username': username,
                }
            }
            json_message = json.dumps(audio_data)
            # Broadcast the audio message to other clients in the room
            if room in rooms:
                            room_clients = rooms[room]
                            for _, client_socket in room_clients:
                                if client_socket != sender_socket:
                                    try:
                                        WebSocket.send_audio(client_socket, json_message)
                                    except Exception as e:
                                        print(f"Error broadcasting file: {e}")
                                        remove_client(_, room, client_socket)
        except Exception as e:
            print(f"Error preparing audio data for broadcast: {e}")

    