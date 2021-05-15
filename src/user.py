from typing import List, Optional
import socket

from src import constants
from src.byte_message_type import ByteMessageType
from src.chat import Chat
from src.chat_info import ChatInfo
from src.chat_manager import ChatManager
from src.chat_message import ChatMessage
from src.chat_message_type import ChatMessageType
from src.dht.hash_table import HashTable
from src.message_builders.message_builder import MessageBuilder
from src.message_redirection import MessageRedirection
from src.preferences import Preferences
from src.senders.socket_message_sender import SocketMessageSender
from src.user_info import UserInfo


class User:

    def __init__(self, username: Optional[str] = None):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.ip = socket.inet_aton(self.ip)
        self.port = 8090 + constants.random_int(1)

        self.network_invite_link: Optional[str] = None

        self.preferences = Preferences()
        self.username = username

        self.chat_manager = ChatManager()
        self.message_redirection = MessageRedirection()
        self.socket_message_sender = SocketMessageSender(self.ip, self.port, self.message_redirection.handle,
                                                         self.message_redirection.handle)

        self.user_id = constants.random_int(constants.ID_LENGTH)
        self.user_info = UserInfo(self.user_id, self.username, self.ip, self.port)
        self.hash_table = HashTable(self.user_id, self.socket_message_sender, self.message_redirection)

        self._configure_message_redirection()

    def _load_chats(self) -> None:
        chat_info = ChatInfo()
        chats: List[ChatInfo] = self.preferences.load_array_of_objects("chats", chat_info)

        for chat in chats:
            if self._join_chat(chat.chat_id, chat.private_key) is None:
                self._push_chat_to_hash_table(Chat(chat.chat_id, chat.chat_name, chat.private_key))

    def _configure_message_redirection(self) -> None:
        self.message_redirection.subscribe(ByteMessageType.CHAT_MESSAGE, self.chat_manager.handle_message)

    def create_chat(self, chat_name: str) -> int:
        chat = self.chat_manager.create_chat(chat_name)
        self._push_chat_to_hash_table(chat)

        chat_info = ChatInfo(chat.chat_id, chat.chat_name, chat.private_key)
        self.preferences.save_object_to_array("chats", "chat_id", chat_info)
        return chat.chat_id

    def _push_chat_to_hash_table(self, chat: Chat) -> None:
        self._add_chat(chat)
        self.hash_table.set_value(ChatMessageType.SET_CHAT_NAME, chat.chat_id,
                                  chat.build_chat_name_message())

        introduce_message = chat.build_introduce_message(self.user_info)
        self._broadcast_message(chat.chat_id, introduce_message)

    def get_invite_link(self, chat_id: int) -> str:
        return self.chat_manager.get_invite_link(chat_id)

    def set_network_invite_link(self, invite_link: str):
        self.network_invite_link = invite_link

    def get_network_invite_link(self) -> str:
        return self.hash_table.get_invite_link()

    def join_network_by_invite_link(self) -> None:
        self.hash_table.join(self.network_invite_link)
        self._load_chats()

    @staticmethod
    def _build_get_chat_message(chat_id: int) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.CHAT_MESSAGE) \
            .append_id(chat_id) \
            .append_type(ChatMessageType.GET_CHAT) \
            .build()

    def _broadcast_message(self, chat_id: int, message: bytes) -> None:
        self.hash_table.append_value(ChatMessageType.TEXT_MESSAGE, chat_id, message)

    def join_chat_by_link(self, invite_link: str) -> int:
        print(invite_link)
        chat_id, private_key = self.chat_manager.parse_invite_link(invite_link)

        if chat_id in self.chat_manager.get_chat_id_list():
            return chat_id

        chat = self._join_chat(chat_id, private_key)

        self.preferences.save_object_to_array("chats", "chat_id", ChatInfo(chat_id, chat.chat_name, private_key))
        return chat.chat_id

    def _join_chat(self, chat_id: int, private_key: bytes) -> Optional[Chat]:
        chat = Chat()

        chat_name_message = self.hash_table.get_single_value(ChatMessageType.SET_CHAT_NAME, chat_id)
        if chat_name_message == b'':
            return None

        chat.load(chat_id, private_key, chat_name_message)

        self._add_chat(chat)

        messages = self.hash_table.get_all_values(ChatMessageType.TEXT_MESSAGE, chat_id)
        for message in messages:
            self.socket_message_sender.handle_message(message)

        message = self.chat_manager.build_introduce_message(chat_id, self.user_info)
        self._broadcast_message(chat_id, message)

        return chat

    def _add_chat(self, chat: Chat) -> None:
        self.chat_manager.add_chat(chat)
        self.hash_table.subscribe(chat.chat_id, ChatMessageType.TEXT_MESSAGE)

    def send_text_message(self, chat_id: int, data: str) -> None:
        data = data.encode("utf-8")
        message = self.chat_manager.build_send_text_message(
            chat_id,
            ChatMessage(ChatMessageType.TEXT_MESSAGE, self.username, data)
        )
        self._broadcast_message(chat_id, message)

    def get_chat_id_list(self) -> List[int]:
        return self.chat_manager.get_chat_id_list()

    def get_chat_info(self, chat_id: int) -> Chat:
        return self.chat_manager.get_chat_info(chat_id)

    def get_user_id_list(self, chat_id: int) -> List[UserInfo]:
        return self.chat_manager.get_user_id_list(chat_id)

    def get_message_list(self, chat_id: int) -> List[ChatMessage]:
        return self.chat_manager.get_message_list(chat_id)

    def get_username(self) -> Optional[str]:
        username = self.preferences.load_primitive_type("username")
        self.username = username
        self.user_info.user_name = username
        return self.username

    def get_ip(self) -> bytes:
        return self.ip

    def get_id(self) -> int:
        return self.user_id

    def set_username(self, username: str) -> None:
        self.username = username
        self.user_info.user_name = username
        self.preferences.save_object("username", username)

    def find_username(self, user_id: int) -> str:
        return "TO DO"

    def __del__(self):
        self.socket_message_sender.__del__()
