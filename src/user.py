import os
from typing import List

from src import constants
from src.byte_message_type import ByteMessageType
from src.chat import Chat
from src.chat_manager import ChatManager
from src.chat_message_type import ChatMessageType
from src.message_builders.message_builder import MessageBuilder
from src.message_redirection import MessageRedirection
from src.senders.local_message_sender import LocalMessageSender
from src.text_message import TextMessage
from src.user_info import UserInfo


class User:

    def __init__(self, username: str):
        self.ip = os.urandom(3)
        self.user_id = constants.random_int(constants.ID_LENGTH)
        self.username = username

        self.chat_manager = ChatManager()
        self.message_redirection = MessageRedirection()
        self.byte_message_socket = LocalMessageSender(self.ip, self.message_redirection.handle,
                                                      self.message_redirection.handle)

        self._configure_message_redirection()

    def _configure_message_redirection(self) -> None:
        self.message_redirection.subscribe(ByteMessageType.CHAT_MESSAGE, self.chat_manager.handle_message)

    def create_chat(self, chat_name: str) -> None:
        self.chat_manager.create_chat(self.ip, self.user_id, chat_name)

    def get_invite_link(self, chat_id: int) -> str:
        return self.chat_manager.get_invite_link(chat_id, self.ip)

    def _build_introduce_message(self, chat_id: int) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id) \
            .append_type(ChatMessageType.INTRODUCE_USER) \
            .append_serializable(UserInfo(self.user_id, self.ip)) \
            .build()

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
            self.byte_message_socket.send_message(address.ip, message)

    def join_chat_by_link(self, invite_link: str) -> None:
        chat_id, private_key, ip = self.chat_manager.parse_invite_link(invite_link)

        message = self._build_get_chat_message(chat_id)
        chat_data = self.byte_message_socket.send_request(ip, message)
        chat = self.chat_manager.parse_chat_data(chat_data, private_key)
        self.chat_manager.add_chat(chat)

        message = self._build_introduce_message(chat_id)
        self._broadcast_message(chat_id, message)
        # Then send myself
        self.byte_message_socket.send_message(self.ip, message)

    def _build_send_text_message(self, chat_id: int, data: str) -> bytes:
        data = data.encode("utf-8")
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id) \
            .append_type(ChatMessageType.TEXT_MESSAGE) \
            .append_serializable(TextMessage(self.user_id, data)) \
            .build()

    def send_text_message(self, chat_id: int, data: str) -> None:
        message = self._build_send_text_message(chat_id, data)
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
