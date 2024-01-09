from flask import Blueprint, jsonify
from chat_server import ChatServer

PORT = 5050
routes = Blueprint("routes", __name__)
server = ChatServer(PORT)

routes.route('/get_usernames', methods=['GET'])
def get_usernames():
    usernames = server.get_usernames()
    return jsonify({'usernames': usernames})

routes.route('/test')
def test():
    print('test')
    return True

routes.route('/')
def home():
    return 'Hello, World!'

