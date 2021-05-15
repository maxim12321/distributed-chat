import base64
from typing import Dict, List, Optional, Tuple

from src import constants
from src.chat import Chat
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.chat_message import ChatMessage
from src.user_info import UserInfo


class ChatManager:

    def __init__(self):
        self.chat_list: Dict[int, Chat] = dict()

    def add_chat(self, chat: Chat) -> None:
        self.chat_list[chat.get_chat_id()] = chat

    @staticmethod
    def create_chat(chat_name: str) -> Chat:
        chat = Chat()
        chat.create(chat_name)
        return chat

    def handle_message(self, message: bytes) -> Optional[bytes]:
        chat_id = Container[int]()

        message = MessageParser.parser(message) \
            .append_id(chat_id) \
            .parse()

        if chat_id.get() in self.chat_list:
            return self.chat_list[chat_id.get()].handle_message(message)

    def get_invite_link(self, chat_id: int) -> str:
        invite_link = self.chat_list[chat_id].generate_invite_link()
        return constants.base64_to_url(invite_link)

    def get_chat_id_list(self) -> List[int]:
        return list(self.chat_list.keys())

    def get_chat_info(self, chat_id: int) -> Chat:
        return self.chat_list[chat_id]

    def get_user_id_list(self, chat_id: int) -> List[UserInfo]:
        return self.chat_list[chat_id].message_handler.get_user_id_list()

    def get_message_list(self, chat_id: int) -> List[ChatMessage]:
        return self.chat_list[chat_id].get_message_list()

    @staticmethod
    def parse_invite_link(invite_link: str) -> Tuple[int, bytes]:
        invite_link = constants.url_to_base64(invite_link)
        invite_link = base64.b64decode(invite_link)

        chat_id: Container[int] = Container()
        private_key: Container[bytes] = Container()

        MessageParser.parser(invite_link) \
            .append_id(chat_id) \
            .append_bytes(private_key) \
            .parse()

        return chat_id.get(), private_key.get()

    @staticmethod
    def parse_chat_data(chat_data: bytes, private_key: bytes) -> Chat:
        chat = Chat()

        MessageParser.parser(chat_data) \
            .begin_encrypted(private_key) \
            .append_serializable(chat) \
            .encrypt() \
            .parse()

        return chat

    def build_send_images(self, chat_id: int, images: ChatMessage) -> bytes:
        return self.chat_list[chat_id].build_send_images(images)

    def build_send_text_message(self, chat_id: int, text_message: ChatMessage) -> bytes:
        return self.chat_list[chat_id].build_send_text_message(text_message)

    def build_introduce_message(self, chat_id: int, user_info: UserInfo) -> bytes:
        return self.chat_list[chat_id].build_introduce_message(user_info)
