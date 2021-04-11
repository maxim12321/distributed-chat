from text_message import TextMessage
from user_info import UserInfo
from typing import List
import constants


class MessageHandler:
    def __init__(self):
        self.users: List[UserInfo] = []
        self.messages: List[TextMessage] = []

    def __iter__(self):
        yield from {
            "user_info_list": [dict(user_info) for user_info in self.users],
            "message_list": [dict(messages) for messages in self.messages],
        }.items()

    def load_from_dict(self, data: dict) -> None:
        messages_dict = data["message_list"]
        user_info_dict = data["user_info_list"]
        for message in messages_dict:
            self.messages.append(TextMessage(message["sender_id"], message["context"]))
        for user_info in user_info_dict:
            self.users.append(UserInfo(user_info["user_id"]))

    def handle_text_message(self, message: bytes) -> None:
        sender_id = constants.to_int(message[:constants.ID_LENGTH])
        text_message = message[constants.ID_LENGTH:]
        self.messages.append(TextMessage(sender_id, text_message))

    def handle_introduce_user(self, message_id: bytes) -> None:
        self.users.append(UserInfo(constants.to_int(message_id)))

    def handle_user_list(self, message: bytes) -> None:
        self.users.clear()
        for current_byte in range(0, len(message), constants.ID_LENGTH):
            user_id_bytes = message[current_byte:current_byte + constants.ID_LENGTH]
            self.users.append(UserInfo(constants.to_int(user_id_bytes)))

    def get_user_id_list(self) -> List[UserInfo]:
        return self.users

    def get_messages(self) -> List[TextMessage]:
        return self.messages
