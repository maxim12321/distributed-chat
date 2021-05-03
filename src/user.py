import base64
import os

from src import constants
from src.senders.local_message_sender import LocalMessageSender
from src.message_redirection import MessageRedirection
from src.request_redirection import RequestRedirection
from src.byte_message_type import ByteMessageType
from src.chat_message_type import ChatMessageType
from src.chat_manager import ChatManager
from src.chat import Chat
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.message_builders.message_builder import MessageBuilder
from src.user_info import UserInfo
from src.text_message import TextMessage
from typing import List


class User:
    def __init__(self):
        self.ip = os.urandom(3)
        self.user_id = constants.random_int(constants.ID_LENGTH)
        self.username = "Squirrel"

        self.chat_manager = ChatManager()
        self.message_redirection = MessageRedirection()
        self.request_redirection = RequestRedirection()
        self.byte_message_socket = LocalMessageSender(self.ip, self.message_redirection.handle,
                                                      self.request_redirection.handle)

        self.subscribe()

    def subscribe(self) -> None:
        self.request_redirection.subscribe(ByteMessageType.CHAT_MESSAGE, self.chat_manager.handle_message)
        self.message_redirection.subscribe(ByteMessageType.CHAT_MESSAGE, self.chat_manager.handle_message)

    def create_chat(self, chat_name: str) -> None:
        self.chat_manager.create_chat(self.ip, self.user_id, chat_name)

    def get_invite_link(self, chat_id: int) -> str:
        return self.chat_manager.get_invite_link(chat_id, self.ip)

    def join_chat_by_link(self, invite_link: str) -> None:
        link = base64.b64decode(invite_link)

        chat_id: Container[int] = Container()
        private_key: Container[bytes] = Container()
        ip: Container[bytes] = Container()

        MessageParser.parser(link) \
            .append_id(chat_id) \
            .append_bytes(private_key) \
            .append_bytes(ip) \
            .parse()

        message = MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id.get()) \
            .append_type(ChatMessageType.GET_CHAT) \
            .build()

        chat_data = self.byte_message_socket.send_request(ip.get(), message)
        chat = Chat()

        MessageParser.parser(chat_data) \
            .begin_encrypted(private_key.get()) \
            .append_serializable(chat) \
            .encrypt() \
            .parse()

        message = MessageBuilder.builder() \
            .append_type(ChatMessageType.INTRODUCE_USER) \
            .append_serializable(UserInfo(self.user_id, self.ip)) \
            .build()

        chat.handle_message(message)

        message = MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id.get()) \
            .append_type(ChatMessageType.INTRODUCE_USER) \
            .append_serializable(UserInfo(self.user_id, self.ip)) \
            .build()

        addresses = chat.message_handler.get_user_id_list()

        for address in addresses:
            self.byte_message_socket.send_message(address.ip, message)

        self.chat_manager.add_chat(chat)

    def send_text_message(self, chat_id: int, data: str) -> None:
        data = data.encode("utf-8")
        message = MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id) \
            .append_type(ChatMessageType.TEXT_MESSAGE) \
            .append_serializable(TextMessage(self.user_id, data)) \
            .build()

        addresses = self.chat_manager.get_user_id_list(chat_id)

        for address in addresses:
            self.byte_message_socket.send_message(address.ip, message)

    def get_chat_list(self):
        return self.chat_manager.get_chat_list()

    def get_user_id_list(self, chat_id: int) -> List[UserInfo]:
        return self.chat_manager.get_user_id_list(chat_id)

    def get_messages(self, chat_id: int) -> List[TextMessage]:
        return self.chat_manager.get_messages(chat_id)
