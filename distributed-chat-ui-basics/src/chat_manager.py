from chat import Chat
import constants


class ChatManager:
    def __init__(self):
        self.chat_list = dict()

    def add_chat(self, chat: Chat) -> None:
        self.chat_list[chat.get_chat_id()] = chat

    def create_chat(self, user_id: bytes, chat_name: str) -> Chat:
        chat = Chat(user_id, chat_name)
        self.chat_list[chat.get_chat_id()] = chat
        return chat

    def handle_message(self, message: bytes) -> None:
        chat_id = message[:constants.ID_LENGTH]
        if chat_id in self.chat_list:
            self.chat_list[chat_id].handle_message(message[constants.ID_LENGTH:])
