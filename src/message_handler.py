from serializable import Serializable
from text_message import ChatMessage
from user_info import UserInfo
from typing import List

from src.message_builders.message_builder import MessageBuilder
from src.chat_message_type import ChatMessageType
from src.message_parsers.message_parser import MessageParser
from src.message_parsers.container import Container
from src.image_manager import ImageManager
import constants


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
            self.messages.append(ChatMessage(message.type, message["sender_id"], message["context"]))
        for user_info in data["user_info_list"]:
            self.users.append(UserInfo(user_info["user_id"]))

    def handle_text_message(self, message: bytes) -> None:
        sender_id = Container[int]()
        text_message = Container[bytes]()
        MessageParser.parser(message) \
            .append_id(sender_id) \
            .append_bytes(text_message) \
            .parse()
        self.messages.append(ChatMessage(ChatMessageType.TEXT_MESSAGE, sender_id.get(), text_message.get()))

    def handle_introduce_user(self, message_id: bytes) -> None:
        user_id = Container[int]()
        MessageParser.parser(message_id) \
            .append_id(user_id) \
            .parse()
        self.users.append(UserInfo(user_id))

    def handle_user_list(self, message: bytes) -> None:
        self.users.clear()
        for current_byte in range(0, len(message), constants.ID_LENGTH):
            user_id_bytes = message[current_byte:current_byte + constants.ID_LENGTH]
            self.users.append(UserInfo(constants.to_int(user_id_bytes)))

    def handle_image(self, message: bytes) -> None:
        sender_id = Container[int]()
        image_hashes = MessageParser.parser(message) \
            .append_id(sender_id) \
            .parse()
        self.messages.append(ChatMessage(ChatMessageType.IMAGE, sender_id.get(), image_hashes))

    def handle_image_hashes(self, message: bytes) -> bytes:
        sender_id = Container[int]()
        context = Container[List[str]]()
        MessageParser.parser(message) \
            .append_id(sender_id) \
            .append_object(context) \
            .parse()

        images = self.image_manager.get_images(context.get())
        return MessageBuilder.builder() \
            .append_bytes_list(images) \
            .build()

    def get_user_id_list(self) -> List[UserInfo]:
        return self.users

    def get_messages(self) -> List[ChatMessage]:
        return self.messages
