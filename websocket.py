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

    
    @staticmethod
    def send_connected_users(client_socket, connected_users):
        try:
            # Convert the list of connected users to JSON
            users_json = json.dumps(connected_users)

            message_length = len(users_json)
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

            frame.extend(users_json.encode('utf-8'))
            client_socket.send(frame)

        except Exception as e:
            print(f"Error sending connected users: {e}")

    
    @staticmethod
    def send_file(client_socket, json_message):
        try:
            # Convert the JSON message to bytes
            message_bytes = json_message.encode('utf-8')

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
            print(f"Error sending file: {e}")


    @staticmethod
    def send_audio(client_socket, audio_content):
        try:
            # Parse the JSON string to a dictionary
            audio_data = json.loads(audio_content)

            # Get the raw audio data from the "audio" key
            raw_audio_data = audio_data.get('audio', {}).get('content')

            if raw_audio_data is not None:
                # Prepare the audio message to be sent
                audio_message = {
                    'type': 'audio',
                    'audio': {
                        'content': raw_audio_data,
                        'username': audio_data.get('audio', {}).get('username', ''),  # Include username if available
                    }
                }
                # Convert the audio message to JSON bytes
                json_message = json.dumps(audio_message).encode('utf-8')

                message_length = len(json_message)
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

                frame.extend(json_message)
                client_socket.send(frame)

        except Exception as e:
            print(f"Error sending audio: {e}")
