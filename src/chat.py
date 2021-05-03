from typing import Optional, Generator, Any
from dataclasses import dataclass
from serializable import Serializable
from src.message_handler import MessageHandler
from src.chat_message_type import ChatMessageType
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.message_builders.message_builder import MessageBuilder
import os
import base64
import constants


@dataclass
class Chat(Serializable):

    def __init__(self):
        self.message_handler = MessageHandler()
        self.private_key: Optional[bytes] = None
        self.chat_name: Optional[str] = None
        self.chat_id: Optional[int] = None

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "chat_id": self.chat_id,
            "chat_name": self.chat_name,
            "private_key": constants.bytes_to_dict(self.private_key),
            "message_handler": dict(self.message_handler)
        }.items()

    def create(self, chat_name: str) -> None:
        self.chat_id = constants.random_int(constants.ID_LENGTH)
        self.private_key = os.urandom(constants.PRIVATE_KEY_LENGTH)
        self.chat_name = chat_name

    def load_from_dict(self, data_dict: dict) -> None:
        self.chat_id = data_dict["chat_id"]
        self.private_key = data_dict["private_key"]
        self.chat_name = data_dict["chat_name"]
        self.message_handler.load_from_dict(data_dict["message_handler"])

    def generate_invite_link(self, ip_address: bytes) -> str:
        link = MessageBuilder.builder() \
            .append_id(self.chat_id) \
            .append_bytes(self.private_key) \
            .append_bytes(ip_address) \
            .build()
        return base64.b64encode(link).decode("utf-8")

    def handle_message(self, message: bytes) -> Optional[bytes]:
        message_type = Container[ChatMessageType]()

        message = MessageParser.parser(message) \
            .append_type(message_type) \
            .parse()

        if message_type.get() == ChatMessageType.TEXT_MESSAGE:
            self.message_handler.handle_text_message(message)
            return None

        if message_type.get() == ChatMessageType.INTRODUCE_USER:
            self.message_handler.handle_introduce_user(message)
            return None

        if message_type.get() == ChatMessageType.GET_CHAT:
            message = MessageBuilder.builder() \
                .begin_encrypted() \
                .append_serializable(self) \
                .encrypt(self.private_key) \
                .build()
            return message

    def get_chat_id(self) -> int:
        return self.chat_id
