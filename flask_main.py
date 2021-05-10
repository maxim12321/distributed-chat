import json

from flask import Flask, jsonify
from src.user import User

app = Flask(__name__)
user = User()


@app.route('/')
def hello_world() -> str:
    return 'Hello chat!'


@app.route('/set_username/<username>')
def set_username(username: str) -> str:
    user.set_username(username)
    return 'OK'


@app.route('/get_username/<user_id>')
def get_username(user_id: str) -> str:
    user_id = int(user_id)
    if user_id == -1:
        return user.get_username()
    return user.find_username(user_id)


@app.route('/get_chat_id_list')
def get_chat_id_list() -> str:
    return jsonify(user.get_chat_id_list())


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
def gAddet_message_list(chat_id: int) -> str:
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
