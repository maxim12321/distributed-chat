from text_message import TextMessage
from user_info import UserInfo
from typing import List
import constants


class MessageHandler:
    def __init__(self):
        self.user_info_list: List[UserInfo] = []
        self.message_list: List[TextMessage] = []

    def __iter__(self):
        message_handler_dict = dict()
        message_handler_dict["user_info_list"] = []
        message_handler_dict["message_list"] = []
        for user_info in self.user_info_list:
            message_handler_dict["user_info_list"].append(dict(user_info))
        for messages in self.message_list:
            message_handler_dict["message_list"].append(dict(messages))

        yield from message_handler_dict.items()

    def load_from_dict(self, data_dict: dict) -> None:
        messages_dict = data_dict["message_list"]
        user_info_dict = data_dict["user_info_list"]
        for message in messages_dict:
            self.message_list.append(TextMessage(message["sender_id"], message["context"]))
        for user_info in user_info_dict:
            self.user_info_list.append(UserInfo(user_info["user_id"]))

    def handle_text_message(self, message: bytes) -> None:
        sender_id = constants.to_int(message[:constants.ID_LENGTH])
        text_message = message[constants.ID_LENGTH:]
        self.message_list.append(TextMessage(sender_id, text_message))

    def handle_introduce_user(self, message_id: bytes) -> None:
        self.user_info_list.append(UserInfo(constants.to_int(message_id)))

    def handle_user_list(self, message: bytes) -> None:
        self.user_info_list.clear()
        for current_byte in range(0, len(message), constants.ID_LENGTH):
            self.user_info_list.append(
                UserInfo(constants.to_int(message[current_byte:current_byte + constants.ID_LENGTH])))

    def get_user_id_list(self) -> List[UserInfo]:
        return self.user_info_list

    def get_messages(self) -> List[TextMessage]:
        return self.message_list
