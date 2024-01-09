#websocket.py
import base64
import hashlib

OPCODE_TEXT_FRAME = 0x81
PAYLOAD_LEN_7_BITS = 0x7D
PAYLOAD_LEN_16_BITS = 0x7E
PAYLOAD_LEN_64_BITS = 0x7F

class WebSocket:
    @staticmethod
    def calculate_websocket_key(key):
        GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        concatenated = key + GUID
        hashed = hashlib.sha1(concatenated.encode())
        response_key = hashed.digest()
        return base64.b64encode(response_key).decode('utf-8')

    @staticmethod
    def send_message(client_socket, message):
        try:
            message_length = len(message)
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

            frame.extend(message.encode('utf-8'))
            client_socket.send(frame)

        except Exception as e:
            print(f"Error sending message: {e}")
