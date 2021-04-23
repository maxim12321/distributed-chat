import os

from byte_message_socket import ByteMessageSocket
from message_redirection import MessageRedirection
from request_redirection import RequestRedirection
from chat_manager import ChatManager


class User:
    def __init__(self):
        self.user_id = os.urandom(16)
        self.chat_manager = ChatManager(self.user_id)
        self.message_redirection = MessageRedirection()
        self.request_redirection = RequestRedirection()
        self.byte_message_socket = ByteMessageSocket(self.message_redirection, self.request_redirection)
        self.my_ip = self.byte_message_socket.get_ip()
        self.chord = "Макс запушь ради христа"
        self.username = "Squirrel"

    def create_chat(self, chat_name: str) -> None:
        self.chat_manager.create_chat(chat_name)

    def get_invite_link(self, chat_id: int) -> str:
        return self.chat_manager.get_invite_link(chat_id, self.my_ip)

    def join_chat(self, invite_link: str) -> None:
        self.chat_manager.join_chat(invite_link)

    def get_chat_list(self):
        return self.chat_manager.get_chat_list()

    def send_text_message(self, chat_id: int, message: str) -> None:
        self.chat_manager.send_text_message(chat_id, message)
