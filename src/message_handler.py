from src.message_builders.message_builder import MessageBuilder
from src.chat_message_type import ChatMessageType
from src.message_parsers.container import Container
from src.image_manager import ImageManager
from typing import List

from src.message_parsers.message_parser import MessageParser
from src.serializable import Serializable
from src.text_message import ChatMessage
from src.user_info import UserInfo


class MessageHandler(Serializable):

    def __init__(self):
        self.users: List[UserInfo] = []
        self.messages: List[ChatMessage] = []
        self.image_manager = ImageManager()

    def __iter__(self):
        yield from {
            "user_info_list": [dict(user_info) for user_info in self.users],
            "message_list": [dict(messages) for messages in self.messages],
        }.items()

    def load_from_dict(self, data: dict) -> None:
        self.messages.clear()
        self.users.clear()
        for message in data["message_list"]:
            self.messages.append(ChatMessage.from_dict(message))
        for user_info in data["user_info_list"]:
            self.users.append(UserInfo.from_dict(user_info))

    def handle_text_message(self, message: bytes, private_key: bytes) -> None:
        text_message = ChatMessage()
        MessageParser.parser(message) \
            .begin_encrypted(private_key) \
            .append_serializable(text_message) \
            .encrypt() \
            .parse()
        self.messages.append(text_message)

    def handle_introduce_user(self, message_id: bytes, private_key: bytes) -> None:
        user_info = UserInfo()
        MessageParser.parser(message_id) \
            .begin_encrypted(private_key) \
            .append_serializable(user_info) \
            .encrypt() \
            .parse()
        self.users.append(user_info)

    def handle_image(self, message: bytes, private_key: bytes) -> None:
        sender_id = Container[int]()
        image_hashes = MessageParser.parser(message) \
            .begin_encrypted(private_key) \
            .append_id(sender_id) \
            .encrypt() \
            .parse()
        self.messages.append(ChatMessage(ChatMessageType.IMAGE, sender_id.get(), image_hashes))

    def handle_image_hashes(self, message: bytes, private_key: bytes) -> bytes:
        sender_id = Container[int]()
        context = Container[List[str]]()
        MessageParser.parser(message) \
            .begin_encrypted(private_key) \
            .append_id(sender_id) \
            .append_object(context) \
            .encrypt() \
            .parse()

        images = self.image_manager.get_images(context.get())
        return MessageBuilder.builder() \
            .append_bytes_list(images) \
            .build()

    def get_user_id_list(self) -> List[UserInfo]:
        return self.users

    def get_message_list(self) -> List[ChatMessage]:
        return self.messages
