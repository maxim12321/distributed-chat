from chat import Chat
import constants
import base64


class ChatManager:
    def __init__(self, user_id: bytes):
        self.chat_list = dict()
        self.user_id = user_id

    # def add_chat(self, chat: Chat) -> None:
    #     self.chat_list[chat.get_chat_id()] = chat

    def create_chat(self, chat_name: str) -> None:
        chat = Chat(user_id=self.user_id, chat_name=chat_name)
        self.chat_list[chat.get_chat_id()] = chat

    def handle_message(self, message: bytes) -> None:
        chat_id = message[:constants.ID_LENGTH]
        if chat_id in self.chat_list:
            self.chat_list[chat_id].handle_message(message[constants.ID_LENGTH:])

    def get_invite_link(self, chat_id: int, my_ip: str) -> str:
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