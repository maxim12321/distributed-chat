from chat_message_type import ChatMessageType
from typing import Dict
from chat import Chat
import constants
import base64


class ChatManager:
    def __init__(self):
        self.chat_list: Dict[int, Chat] = dict()

    # def add_chat(self, chat: Chat) -> None:
    #     self.chat_list[chat.get_chat_id()] = chat

    def create_chat(self, user_id: int, chat_name: str) -> Chat:
        chat = Chat()
        chat.create(chat_name)
        chat.handle_message(constants.message_type_to_bytes(ChatMessageType.INTRODUCE_USER)
                            + constants.id_to_bytes(user_id))
        self.chat_list[chat.get_chat_id()] = chat

    def handle_message(self, message: bytes) -> None:
        chat_id = constants.to_int(message[:constants.ID_LENGTH])
        if chat_id in self.chat_list:
            self.chat_list[chat_id].handle_message(message[constants.ID_LENGTH:])

    def get_invite_link(self, chat_id: int, my_ip: bytes) -> str:
        return self.chat_list[chat_id].generate_invite_link(my_ip)

    def parse_invite_link(self, link: str) -> any:
        link_bytes = base64.b64decode(link)
        self.chat_id = link_bytes[:constants.ID_LENGTH]
        self.private_key = link_bytes[constants.ID_LENGTH:constants.ID_LENGTH + constants.PRIVATE_KEY_LENGTH]
        return self.chat_id, self.private_key

    def join_chat(self, invite_link: str) -> None:
        chat_id, private_key = self.parse_invite_link(invite_link)
        chat = Chat()
        self.chat_list[chat.get_chat_id()] = chat

    def get_chat_list(self):
        return self.chat_list

    def send_text_message(self, chat_id: int, message: str) -> None:
        self.chat_list[chat_id].send_text_message(message)