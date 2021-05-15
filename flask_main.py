import json
from typing import Optional, List

from flask import Flask, jsonify, request, redirect
from flask_cors import cross_origin, CORS

from src.chat_message_type import ChatMessageType
from src.image_manager import ImageManager
from src.user import User


UI_BASE_URL: str = "http://localhost:3000"


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

user = User()


@app.route('/')
@cross_origin()
def main_page() -> str:
    network_invite_link = request.args["network"] if "network" in request.args else None

    if network_invite_link is not None:
        user.set_network_invite_link(network_invite_link)

    username = user.get_username()
    if username is None:
        return redirect(UI_BASE_URL + "/login", code=302)

    user.join_network_by_invite_link()
    return redirect(UI_BASE_URL, code=302)


@app.route('/join_chat')
@cross_origin()
def join_chat() -> str:
    invite_link = request.args["link"]
    user.join_chat_by_link(invite_link)
    return redirect(UI_BASE_URL, code=302)


@app.route('/send', methods=['POST'])
@cross_origin()
def send_message() -> str:
    text = request.json["text"]
    chat_id = int(request.json["chat_id"])
    user.send_text_message(chat_id, text)
    return 'OK'


@app.route('/send_images', methods=['POST'])
@cross_origin()
def send_images() -> str:
    image_urls = request.json["image_urls"]
    image_manager = ImageManager()
    image_manager.save_images(image_urls)
    return 'OK'


@app.route('/set_username', methods=['POST'])
@cross_origin()
def set_username() -> str:
    username = request.json["user_name"]
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
            "isMe": chat_message.sender_name == user.username,
            "user": {
                "_id": 228,
                "fullname": chat_message.sender_name,
                "avatar": None
            }
        })

    return json.dumps(result)


@app.route('/get_chat_info/<int:chat_id>')
@cross_origin()
def get_chat_info(chat_id: int) -> str:
    temp = dict(user.get_chat_info(chat_id))
    temp = jsonify(temp)
    return temp


@app.route('/get_chat_name')
@cross_origin()
def get_chat_name_by_id() -> str:
    chat_id = int(request.args["chat_id"])
    return user.get_chat_info(chat_id).chat_name


@app.route('/get_invite_link')
@cross_origin()
def get_invite_link_by_id() -> str:
    chat_id = int(request.args["chat_id"])
    return request.host_url + "join_chat?link=" + user.get_chat_info(chat_id).generate_invite_link()


@app.route('/get_network_invite_link')
@cross_origin()
def get_network_invite_link() -> str:
    return request.host_url + "?network=" + user.get_network_invite_link()


@app.route('/create_chat', methods=['POST'])
@cross_origin()
def create_chat() -> str:
    chat_name = request.json["chat_name"]
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


if __name__ == "__main__":
    app.run()
