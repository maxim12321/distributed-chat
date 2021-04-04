from chat import Chat
import constants


class ChatManager:
    def __init__(self):
        self.chat_id_to_chat = {}

    def add_chat(self, chat: Chat):
        self.chat_id_to_chat.update({chat.get_chat_id(): chat})

    def handle_message(self, message: bytes) -> None:
        chat_id = message[:constants.ID_LENGTH]
        if chat_id in self.chat_id_to_chat:
            self.chat_id_to_chat[chat_id].handle_message(message[constants.ID_LENGTH:])
