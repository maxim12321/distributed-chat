import base64
from typing import Dict, List, Optional

from src.chat import Chat
from src.chat_message_type import ChatMessageType
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.text_message import TextMessage
from src.user_info import UserInfo


class ChatManager:

    def __init__(self):
        self.chat_list: Dict[int, Chat] = dict()

    def add_chat(self, chat: Chat) -> None:
        self.chat_list[chat.get_chat_id()] = chat

    def create_chat(self, ip: bytes, user_id: int, chat_name: str) -> None:
        chat = Chat()
        chat.create(chat_name)
        print("1")
        message = MessageBuilder.builder()
        print("2")
        message = message.append_type(ChatMessageType.INTRODUCE_USER)
        print("3")
        message = message.begin_encrypted()
        print("4")
        message = message.append_serializable(UserInfo(user_id, ip))
        print("5")
        message = message.encrypt(chat.private_key)
        print("6")
        message = message.build()
        print("7")
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

    def get_chat_id_list(self) -> List[int]:
        return list(self.chat_list.keys())

    def get_chat_info(self, chat_id: int) -> Chat:
        return self.chat_list[chat_id]

    def get_user_id_list(self, chat_id: int) -> List[UserInfo]:
        return self.chat_list[chat_id].message_handler.get_user_id_list()

    def get_message_list(self, chat_id: int) -> List[TextMessage]:
        return self.chat_list[chat_id].get_message_list()

    def parse_invite_link(self, invite_link: str) -> [int, bytes, bytes]:
        invite_link = base64.b64decode(invite_link)

        chat_id: Container[int] = Container()
        private_key: Container[bytes] = Container()
        ip: Container[bytes] = Container()

        MessageParser.parser(invite_link) \
            .append_id(chat_id) \
            .append_bytes(private_key) \
            .append_bytes(ip) \
            .parse()

        return chat_id.get(), private_key.get(), ip.get()

    def parse_chat_data(self, chat_data: bytes, private_key: bytes) -> Chat:
        chat = Chat()

        MessageParser.parser(chat_data) \
            .begin_encrypted(private_key) \
            .append_serializable(chat) \
            .encrypt() \
            .parse()

        return chat

    def build_send_text_message(self, chat_id: int, text_message: TextMessage) -> bytes:
        return self.chat_list[chat_id].build_send_text_message(text_message)

    def build_introduce_message(self, chat_id: int, user_info: UserInfo) -> bytes:
        return self.chat_list[chat_id].build_introduce_message(user_info)
