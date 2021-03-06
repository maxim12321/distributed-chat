import os
from dataclasses import dataclass
from typing import Any, Generator, List, Optional

from src import constants
from src.byte_message_type import ByteMessageType
from src.chat_message_type import ChatMessageType
from src.message_builders.message_builder import MessageBuilder
from src.message_handler import MessageHandler
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.chat_message import ChatMessage
from src.serializable import Serializable
from src.user_info import UserInfo


@dataclass
class Chat(Serializable):

    def __init__(self, chat_id: Optional[int] = None,
                 chat_name: Optional[str] = None,
                 private_key: Optional[bytes] = None):
        self.chat_id: Optional[int] = chat_id
        self.chat_name: Optional[str] = chat_name
        self.private_key: Optional[bytes] = private_key

        self.message_handler = MessageHandler()

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
        self.chat_name = data_dict["chat_name"]
        self.private_key = data_dict["private_key"]
        self.message_handler.load_from_dict(data_dict["message_handler"])

    def load(self, chat_id: int, private_key: bytes, name_message: bytes) -> None:
        self.chat_id = chat_id
        self.private_key = private_key
        self._load_name(name_message)

    def _load_name(self, name_message: bytes) -> None:
        chat_name: Container[str] = Container()

        MessageParser.parser(name_message) \
            .begin_encrypted(self.private_key) \
            .append_string(chat_name) \
            .encrypt() \
            .parse()

        self.chat_name = chat_name.get()

    def generate_invite_link(self) -> str:
        link = MessageBuilder.builder() \
            .append_id(self.chat_id) \
            .append_bytes(self.private_key) \
            .build()

        invite_link = constants.bytes_to_string(link)
        return constants.base64_to_url(invite_link)

    def save_images(self, image_paths: List[str]) -> List[bytes]:
        return self.message_handler.image_manager.save_images(image_paths)

    def handle_message(self, message: bytes) -> Optional[bytes]:
        message_type = Container[ChatMessageType]()
        message = MessageParser.parser(message) \
            .append_type(message_type) \
            .parse()

        if message_type.get() == ChatMessageType.GET_CHAT:
            message = MessageBuilder.builder() \
                .begin_encrypted() \
                .append_serializable(self) \
                .encrypt(self.private_key) \
                .build()
            return message

        message = MessageParser.parser(message) \
            .begin_encrypted(self.private_key) \
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

        if message_type.get() == ChatMessageType.IMAGE_MESSAGE:
            self.message_handler.handle_image_message(message)
            return None

        if message_type.get() == ChatMessageType.IMAGE_REQUEST:
            return self.message_handler.handle_image_request(message)

    def get_chat_id(self) -> int:
        return self.chat_id

    def get_chat_name(self) -> str:
        return self.chat_name

    def get_user_id_list(self) -> List[UserInfo]:
        return self.message_handler.get_user_id_list()

    def get_message_list(self) -> List[ChatMessage]:
        return self.message_handler.get_message_list()

    def build_chat_name_message(self) -> bytes:
        return MessageBuilder.builder() \
            .begin_encrypted() \
            .append_string(self.chat_name) \
            .encrypt(self.private_key) \
            .build()

    def build_send_text_message(self, text_message: ChatMessage) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(self.chat_id) \
            .append_type(ChatMessageType.TEXT_MESSAGE) \
            .begin_encrypted() \
            .append_serializable(text_message) \
            .encrypt(self.private_key) \
            .build()

    def build_send_images(self, images_message: ChatMessage) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(self.chat_id) \
            .append_type(ChatMessageType.IMAGE_MESSAGE) \
            .begin_encrypted() \
            .append_serializable(images_message) \
            .encrypt(self.private_key) \
            .build()

    def build_introduce_message(self, user_info: UserInfo) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(self.chat_id) \
            .append_type(ChatMessageType.INTRODUCE_USER) \
            .begin_encrypted() \
            .append_serializable(user_info) \
            .encrypt(self.private_key) \
            .build()
