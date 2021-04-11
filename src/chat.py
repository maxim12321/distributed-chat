from typing import Optional, Generator, Any
from dataclasses import dataclass
from message_handler import MessageHandler
from chat_message_type import ChatMessageType
import os
import base64
import constants


@dataclass
class Chat:

    def __init__(self):
        self.message_handler = MessageHandler()
        self.private_key: Optional[bytes] = None
        self.chat_name: Optional[str] = None
        self.chat_id: Optional[int] = None

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "chat_name": self.chat_name,
            "private_key": constants.bytes_to_dict(self.private_key),
            "message_handler": dict(self.message_handler)
        }.items()

    def create(self, chat_name: str):
        self.chat_id = constants.random_int(constants.ID_LENGTH)
        self.private_key = os.urandom(constants.PRIVATE_KEY_LENGTH)
        self.chat_name = chat_name

    def load_from_dict(self, data_dict: dict) -> None:
        key = list(data_dict.keys())[0]
        self.chat_id = key
        data_dict = data_dict[key]
        self.private_key = data_dict["private_key"]
        self.chat_name = data_dict["chat_name"]
        self.message_handler.load_from_dict(data_dict["message_handler"])

    def generate_invite_link(self, ip_address: bytes) -> str:
        link_bytes = base64.b64encode(self.private_key + ip_address)
        return link_bytes.decode("utf-8")

    def parse_invite_link(self, link: str) -> None:
        link_bytes = base64.b64decode(link)
        self.private_key = link_bytes[:constants.PRIVATE_KEY_LENGTH]

    def handle_message(self, message: bytes) -> bytes:
        message_type = ChatMessageType(constants.to_int(message[:constants.MESSAGE_TYPE_BYTE_SIZE]))
        message_content = message[constants.MESSAGE_TYPE_BYTE_SIZE:]
        if message_type == ChatMessageType.TEXT_MESSAGE:
            self.message_handler.handle_text_message(message_content)
            return bytearray()

        if message_type == ChatMessageType.INTRODUCE_USER:
            self.message_handler.handle_introduce_user(message_content)
            user_id_list_bytes = self.get_user_list_message()
            return user_id_list_bytes

        if message_type == ChatMessageType.USER_LIST:
            self.message_handler.handle_user_list(message_content)
            return bytearray()

    def get_user_list_message(self) -> bytes:
        user_id_list = self.message_handler.get_user_id_list()
        user_id_list_bytes = bytearray()
        for user_info in user_id_list:
            user_id_list_bytes += constants.id_to_bytes(user_info.user_id)
        return constants.message_type_to_bytes(ChatMessageType.USER_LIST) + user_id_list_bytes

    def get_introduce_user_message(self, user_id: bytes) -> bytes:
        return constants.message_type_to_bytes(ChatMessageType.INTRODUCE_USER) + user_id

    def get_chat_id(self) -> int:
        return self.chat_id
