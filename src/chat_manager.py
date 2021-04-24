import socket

from chat_message_type import ChatMessageType
from typing import Dict
from chat import Chat
import constants
import base64


class ChatManager:
    def __init__(self, user_id: int):
        self.chat_list: Dict[int, Chat] = dict()
        self.user_id = user_id

    def add_chat(self, chat_id: int, chat: Chat):
        self.chat_list[chat_id] = chat

    def create_chat(self, chat_name: str) -> None:
        chat = Chat()
        chat.create(chat_name)
        chat.handle_message(constants.message_type_to_bytes(ChatMessageType.INTRODUCE_USER)
                            + constants.id_to_bytes(self.user_id))
        self.chat_list[chat.get_chat_id()] = chat

    def handle_message(self, message: bytes) -> None:
        chat_id = constants.to_int(message[:constants.ID_LENGTH])
        if chat_id in self.chat_list:
            self.chat_list[chat_id].handle_message(message[constants.ID_LENGTH:])

    def get_invite_link(self, chat_id: int, my_ip: bytes) -> str:
        return self.chat_list[chat_id].generate_invite_link(my_ip)

    def parse_invite_link(self, link: str) -> any:
        link_bytes = base64.b64decode(link)
        chat_id = link_bytes[:constants.ID_LENGTH]
        private_key = link_bytes[constants.ID_LENGTH:constants.ID_LENGTH + constants.PRIVATE_KEY_LENGTH]
        ip_address = link_bytes[-constants.IP_LENGTH:]
        return chat_id, private_key, ip_address

    def join_chat_by_link(self, invite_link: str) -> None:
        chat_id, private_key, ip = self.parse_invite_link(invite_link)
        chat = Chat()
        chat.private_key = private_key
        chat.chat_id = chat_id
        self.chat_list[chat_id] = chat

    def get_chat_info(self, chat_id: int) -> Chat:
        return self.chat_list[chat_id]

    def get_chat_list(self):
        return self.chat_list
