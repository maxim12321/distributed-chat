from chat_message_type import ChatMessageType
from typing import Dict
from chat import Chat
import constants


class ChatManager:
    def __init__(self):
        self.chat_list: Dict[int, Chat] = dict()

    def add_chat(self, chat: Chat) -> None:
        self.chat_list[chat.get_chat_id()] = chat

    def create_chat(self, user_id: int, chat_name: str) -> Chat:
        chat = Chat()
        chat.create(chat_name)
        chat.handle_message(constants.type_to_bytes(ChatMessageType.INTRODUCE_USER)
                            + constants.id_to_bytes(user_id))
        self.chat_list[chat.get_chat_id()] = chat
        return chat

    def handle_message(self, message: bytes) -> None:
        chat_id = constants.to_int(message[:constants.ID_LENGTH])
        if chat_id in self.chat_list:
            self.chat_list[chat_id].handle_message(message[constants.ID_LENGTH:])
