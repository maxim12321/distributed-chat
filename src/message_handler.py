from serializable import Serializable
from text_message import TextMessage
from user_info import UserInfo
from typing import List
import constants
from src.message_parsers.message_parser import MessageParser


class MessageHandler(Serializable):
    def __init__(self):
        self.users: List[UserInfo] = []
        self.messages: List[TextMessage] = []

    def __iter__(self):
        yield from {
            "user_info_list": [dict(user_info) for user_info in self.users],
            "message_list": [dict(messages) for messages in self.messages],
        }.items()

    def load_from_dict(self, data: dict) -> None:
        self.messages.clear()
        self.users.clear()
        for message in data["message_list"]:
            self.messages.append(TextMessage(message["sender_id"], message["context"]))
        for user_info in data["user_info_list"]:
            self.users.append(UserInfo(user_info["user_id"], user_info["ip"]))

    def handle_text_message(self, message: bytes) -> None:
        text_message = TextMessage()
        MessageParser.parser(message) \
            .append_serializable(text_message) \
            .parse()
        self.messages.append(text_message)

    def handle_introduce_user(self, message_id: bytes) -> None:
        user_info = UserInfo()
        MessageParser.parser(message_id) \
            .append_serializable(user_info) \
            .parse()
        self.users.append(user_info)

    def get_user_id_list(self) -> List[UserInfo]:
        return self.users

    def get_messages(self) -> List[TextMessage]:
        return self.messages
