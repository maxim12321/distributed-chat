import os
from typing import List

import socket

from src import constants
from src.byte_message_type import ByteMessageType
from src.chat import Chat
from src.chat_manager import ChatManager
from src.chat_message_type import ChatMessageType
from src.message_builders.message_builder import MessageBuilder
from src.message_redirection import MessageRedirection
from src.senders.local_message_sender import LocalMessageSender
from src.senders.socket_message_sender import SocketMessageSender
from src.text_message import TextMessage
from src.user_info import UserInfo


class User:

    def __init__(self, username: str):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.ip = socket.inet_aton(self.ip)
        self.port = constants.random_int(2)
        print(self.port)
        self.user_id = constants.random_int(constants.ID_LENGTH)
        self.username = username

        self.chat_manager = ChatManager()
        self.message_redirection = MessageRedirection()
        self.byte_message_socket = SocketMessageSender(self.ip, self.port, self.message_redirection.handle,
                                                      self.message_redirection.handle, self.message_redirection.handle)

        self._configure_message_redirection()

    def _configure_message_redirection(self) -> None:
        self.message_redirection.subscribe(ByteMessageType.CHAT_MESSAGE, self.chat_manager.handle_message)

    def create_chat(self, chat_name: str) -> None:
        self.chat_manager.create_chat(UserInfo(self.user_id, self.ip, self.port), chat_name)

    def get_invite_link(self, chat_id: int) -> str:
        return self.chat_manager.get_invite_link(chat_id, self.ip, self.port)

    @staticmethod
    def _build_get_chat_message(chat_id: int) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id) \
            .append_type(ChatMessageType.GET_CHAT) \
            .build()

    def _broadcast_message(self, chat_id: int, message: bytes) -> None:
        addresses = self.chat_manager.get_user_id_list(chat_id)
        for address in addresses:
            self.byte_message_socket.send_message(address.ip, address.port, message)

    def join_chat_by_link(self, invite_link: str) -> None:
        chat_id, private_key, ip, port = self.chat_manager.parse_invite_link(invite_link)

        message = self._build_get_chat_message(chat_id)
        chat_data = self.byte_message_socket.send_request(ip, port, message)
        chat = self.chat_manager.parse_chat_data(chat_data, private_key)
        self.chat_manager.add_chat(chat)

        message = self.chat_manager.build_introduce_message(chat_id, UserInfo(self.user_id, self.ip, self.port))
        self._broadcast_message(chat_id, message)
        # Then send myself
        self.byte_message_socket.send_message(self.ip, self.port, message)

    def send_text_message(self, chat_id: int, data: str) -> None:
        data = data.encode("utf-8")
        message = self.chat_manager.build_send_text_message(chat_id, TextMessage(self.user_id, data))
        self._broadcast_message(chat_id, message)

    def get_chat_id_list(self) -> List[int]:
        return self.chat_manager.get_chat_id_list()

    def get_chat_info(self, chat_id: int) -> Chat:
        return self.chat_manager.get_chat_info(chat_id)

    def get_user_id_list(self, chat_id: int) -> List[UserInfo]:
        return self.chat_manager.get_user_id_list(chat_id)

    def get_message_list(self, chat_id: int) -> List[TextMessage]:
        return self.chat_manager.get_message_list(chat_id)

    def get_username(self) -> str:
        return self.username

    def get_ip(self) -> bytes:
        return self.ip

    def get_id(self) -> int:
        return self.user_id

    def __del__(self):
        self.byte_message_socket.__del__()
