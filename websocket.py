import base64
import hashlib
import json

# Constants for WebSocket
OPCODE_TEXT_FRAME = 0x81
PAYLOAD_LEN_7_BITS = 0x7D
PAYLOAD_LEN_16_BITS = 0x7E
PAYLOAD_LEN_64_BITS = 0x7F

class WebSocket:
    @staticmethod
    def calculate_websocket_key(key):
        """
        Calculate the WebSocket key for the handshake.

        Args:
            key (str): The Sec-WebSocket-Key received from the client.

        Returns:
            str: The calculated Sec-WebSocket-Accept key to be sent in the handshake response.
        """
        GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        concatenated = key + GUID
        hashed = hashlib.sha1(concatenated.encode())
        response_key = hashed.digest()
        return base64.b64encode(response_key).decode('utf-8')

    @staticmethod
    def send_message(client_socket, content, message_type='text'):
        """
        Send a WebSocket message to the client.

        Args:
            client_socket (socket.socket): The client socket to send the message.
            content (str or dict): The content of the message. If dict, it will be converted to JSON.
            message_type (str): The type of the message ('text' by default).

        Raises:
            Exception: If there is an error in sending the message.
        """
        try:
            # Convert the content to JSON if it's not already
            if not isinstance(content, str):
                content = json.dumps(content)

            message_bytes = content.encode('utf-8')
            message_length = len(message_bytes)
            frame = bytearray()

            frame.append(OPCODE_TEXT_FRAME)
            if message_length <= 125:
                frame.append(message_length)
            elif 126 <= message_length <= 65535:
                frame.extend([PAYLOAD_LEN_16_BITS, (message_length >> 8) & 255, message_length & 255])
            else:
                frame.extend([PAYLOAD_LEN_64_BITS, (message_length >> 56) & 255, (message_length >> 48) & 255,
                              (message_length >> 40) & 255, (message_length >> 32) & 255, (message_length >> 24) & 255,
                              (message_length >> 16) & 255, (message_length >> 8) & 255, message_length & 255])

            frame.extend(message_bytes)
            client_socket.send(frame)

        except Exception as e:
            print(f"Error sending {message_type} message: {e}")
