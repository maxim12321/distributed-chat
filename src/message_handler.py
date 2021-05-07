from typing import List

from src.message_parsers.message_parser import MessageParser
from src.serializable import Serializable
from src.text_message import TextMessage
from src.user_info import UserInfo


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
            self.messages.append(TextMessage.from_dict(message))
        for user_info in data["user_info_list"]:
            self.users.append(UserInfo.from_dict(user_info))

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

    def get_message_list(self) -> List[TextMessage]:
        return self.messages
