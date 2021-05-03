from chat_message_type import ChatMessageType
from typing import Dict, Optional, List
from chat import Chat
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.message_builders.message_builder import MessageBuilder
import constants
from src.user_info import UserInfo
from src.text_message import TextMessage


class ChatManager:
    def __init__(self):
        self.chat_list: Dict[int, Chat] = dict()

    def add_chat(self, chat: Chat) -> None:
        self.chat_list[chat.get_chat_id()] = chat

    def create_chat(self, ip: bytes, user_id: int, chat_name: str) -> None:
        chat = Chat()
        chat.create(chat_name)
        message = MessageBuilder.builder() \
            .append_type(ChatMessageType.INTRODUCE_USER) \
            .append_serializable(UserInfo(user_id, ip)) \
            .build()
        chat.handle_message(message)
        self.chat_list[chat.get_chat_id()] = chat

    def handle_message(self, message: bytes) -> Optional[bytes]:
        chat_id = Container[int]()

        message = MessageParser.parser(message) \
            .append_id(chat_id) \
            .parse()

        if chat_id.get() in self.chat_list:
            return self.chat_list[chat_id.get()].handle_message(message)

    def get_invite_link(self, chat_id: int, ip: bytes) -> str:
        return self.chat_list[chat_id].generate_invite_link(ip)

    def get_chat_list(self):
        return self.chat_list

    def get_user_id_list(self, chat_id: int) -> List[UserInfo]:
        return self.chat_list[chat_id].message_handler.get_user_id_list()

    def get_messages(self, chat_id: int) -> List[TextMessage]:
        return self.chat_list[chat_id].message_handler.get_messages()