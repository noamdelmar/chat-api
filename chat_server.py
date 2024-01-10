import socket
import threading
import logging
from websocket import WebSocket
import json

HOST = '0.0.0.0'

logging.basicConfig(filename='chat_server.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class ChatServer:
    def __init__(self, port):
        self.host = HOST
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.shutdown_flag = threading.Event()

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()

            print(f"Server listening on {self.host}:{self.port}")
            logging.info(f"Server listening on {self.host}:{self.port}")

            while not self.shutdown_flag.is_set():
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()

        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.shutdown_flag.set()
        self.server_socket.close()
        print("Server closed.")
        logging.info("Server closed.")


    def handle_client(self, client_socket, client_address):
        try:
            # Receive and decode the data from the client
            data = client_socket.recv(2048).decode('utf-8')

            # Extract the Sec-WebSocket-Key from the received data
            key = ''
            for line in data.split('\r\n'):
                if 'Sec-WebSocket-Key' in line:
                    key = line.split(': ')[1]

            # Calculate the response key for the WebSocket handshake
            response_key = WebSocket.calculate_websocket_key(key)

            # Send the WebSocket handshake response
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {response_key}\r\n\r\n"
            )
            client_socket.send(response.encode('utf-8'))

            # Receive the username from the client
            # username = 'Oliver'
            username = self.get_username(client_socket)

            # Continue with the rest of your chat application logic
            self.broadcast(f"{username} has joined the chat.", client_socket)

            logging.info(f"New connection from {client_address} - {username}")

            self.clients.append((username, client_socket))

            while True:
                message = self.receive_message(client_socket)
                if not message:
                    break
                self.broadcast(f"{username}: {message}", client_socket)

        except ConnectionResetError:
            pass

        finally:
            connected_usernames = self.get_usernames()
            print(f"Connected users: {', '.join(connected_usernames)}")
            self.remove_client(username, client_socket)
            self.broadcast(f"{username} has left the chat.", client_socket)

    def get_username(self, client_socket):
        try:            
            # Receive the WebSocket message frame
            frame = client_socket.recv(2048)
            
            # Extract the payload from the frame
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
            
            # Unmask the payload
            payload = bytearray()
            for i in range(payload_length):
                payload.append(frame[data_start + i] ^ mask[i % 4])
            
            decoded_payload = payload.decode('utf-8')
            
            data = json.loads(decoded_payload)

            # Check if the received message has the expected 'type' field
            if 'type' in data and data['type'] == 'username':
                return data['username']
            else:
                # Handle unexpected message format
                return None
        except (ConnectionResetError, ValueError, json.JSONDecodeError):
            # Handle errors when receiving or decoding the message
            return None

    def remove_client(self, username, client_socket):
        client_socket.close()
        self.clients.remove((username, client_socket))

    def receive_message(self, client_socket):
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

            return payload.decode('utf-8')

        except (ConnectionResetError, ValueError):
            return None
    
    def broadcast(self, message, sender_socket):
        for _, client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    WebSocket.send_message(client_socket, message)
                except:
                    self.remove_client(_, client_socket)
    
    def get_usernames(self):
        return [username for username, _ in self.clients]
