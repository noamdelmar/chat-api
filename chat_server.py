#chat_server.py
import socket
import threading
from websocket import WebSocket
import logging
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
            username = self.receive_username(client_socket)
            username = 'Oliver'

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
            self.remove_client(username, client_socket)
            self.broadcast(f"{username} has left the chat.", client_socket)

    def receive_username(self, client_socket):
        try:
            # Assuming the client sends the username followed by a newline character
            username = client_socket.recv(1024).decode('utf-8').strip()
            return username
        except (ConnectionResetError, ValueError):
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

            print(payload.decode('utf-8'))
            return payload.decode('utf-8')

        except (ConnectionResetError, ValueError):
            return None
    
    def broadcast(self, message, sender_socket):
        print(message)
        for _, client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    self.remove_client(_, client_socket)
