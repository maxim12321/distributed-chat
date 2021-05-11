import json
from typing import Optional, List

from flask import Flask, jsonify, request
from flask_cors import cross_origin

from src.chat_message_type import ChatMessageType
from src.user import User


app = Flask(__name__)
user = User("Max")

user.join_network_by_invite_link(None)
user.create_chat("Test chat")
user.create_chat("Test chat 2")


@app.route('/<network_invite_link>')
def join_network(network_invite_link: str) -> str:
    return network_invite_link


@app.route('/send', methods=['POST'])
@cross_origin()
def send_message() -> str:
    text = request.json["text"]
    chat_id = int(request.json["chat_id"])
    user.send_text_message(chat_id, text)
    return ""


@app.route('/set_username/<username>')
def set_username(username: str) -> str:
    user.set_username(username)
    return 'OK'


@app.route('/get_username/<user_id>')
def get_username(user_id: str) -> Optional[str]:
    user_id = int(user_id)
    if user_id == -1:
        username = user.get_username()
        return "" if username is None else username
    return user.find_username(user_id)


@app.route('/get_chat_id_list')
@cross_origin()
def get_chat_id_list() -> str:
    result = []
    chat_ids: List[int] = user.get_chat_id_list()

    for chat_id in chat_ids:
        chat_info = user.get_chat_info(chat_id)

        last_message = "No messages yet..."
        if len(chat_info.get_message_list()) > 0:
            last_message = chat_info.get_message_list()[-1].context.decode("utf-8")

        result.append({
            "_id": chat_info.chat_id,
            "user": {
                "fullname": chat_info.get_chat_name()
            },
            "message": {
                "text": last_message,
                "created": "20:30"
            }
        })
    return json.dumps(result)


@app.route('/messages')
@cross_origin()
def get_messages() -> str:
    result = []
    chat_id = int(request.args["dialog"])

    chat_messages = user.get_message_list(chat_id)
    for chat_message in chat_messages:
        if chat_message.type != ChatMessageType.TEXT_MESSAGE:
            continue
        result.append({
            "_id": chat_id,
            "text": chat_message.context.decode("utf-8"),
            "date": "15:30",
            "user": {
                "_id": 228,
                "fullname": chat_message.sender_name,
                "avatar": None
            }
        })

    return json.dumps(result)


@app.route('/get_chat_info/<int:chat_id>')
def get_chat_info(chat_id: int) -> str:
    temp = dict(user.get_chat_info(chat_id))
    temp = jsonify(temp)
    return temp


@app.route('/create_chat/<chat_name>')
def create_chat(chat_name: str) -> str:
    chat_id = user.create_chat(chat_name)
    return str(chat_id)


@app.route('/create_chat_with_user/<int:user_id>')
def create_chat_with_user(user_id: int) -> str:
    return 'TO DO'


@app.route('/get_message_list/<int:chat_id>')
def get_message_list(chat_id: int) -> str:
    temp = user.get_message_list(chat_id)
    temp = json.dumps(temp, default=lambda x: dict(x))
    return temp


@app.route('/send_text_message/<int:chat_id>/<text_message>')
def send_text_message(chat_id: int, text_message: str) -> str:
    user.send_text_message(chat_id, text_message)
    return 'OK'


@app.route('/get_invite_link/<int:chat_id>')
def get_invite_link(chat_id: int) -> str:
    return user.get_invite_link(chat_id)


@app.route('/join_chat/<link>')
def join_chat(link: str) -> str:
    chat_id = user.join_chat_by_link(link)
    return str(chat_id)


if __name__ == "__main__":
    app.run()
