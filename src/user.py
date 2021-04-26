import constants
from byte_message_socket import ByteMessageSocket
from message_redirection import MessageRedirection
from request_redirection import RequestRedirection
from byte_message_type import ByteMessageType
from chat_message_type import ChatMessageType
from chat_manager import ChatManager
from chat import Chat
import socket


class User:
    def __init__(self):
        self.user_id = constants.random_int(constants.ID_LENGTH)
        self.username = "Squirrel"

        self.chat_manager = ChatManager(self.user_id)
        self.message_redirection = MessageRedirection()
        self.request_redirection = RequestRedirection()
        self.byte_message_socket = ByteMessageSocket(self.message_redirection, self.request_redirection)
        self.ip = self.byte_message_socket.get_ip()

        self.subscribe()

    def subscribe(self) -> None:
        self.request_redirection.subscribe(ChatMessageType.GET_CHAT_NAME, self.chat_manager.handle_message)

    def create_chat(self, chat_name: str) -> None:
        self.chat_manager.create_chat(chat_name)

    def get_invite_link(self, chat_id: int) -> str:
        return self.chat_manager.get_invite_link(chat_id, socket.inet_aton(self.ip))

    def join_chat_by_link(self, invite_link: str) -> None:
        chat_id, private_key, ip = self.chat_manager.parse_invite_link(invite_link)
        message = constants.message_type_to_bytes(ChatMessageType.GET_CHAT_NAME)
        message = constants.id_to_bytes(chat_id) + message
        chat = Chat()
        chat.private_key = private_key
        chat.chat_id = chat_id
        name = self.byte_message_socket.send_request(ip, ByteMessageType.CHAT_MESSAGE, message)
        name = constants.bytes_to_string(name)
        chat.chat_name = name
        self.chat_manager.add_chat(chat_id, chat)

    def get_chat_list(self):
        return self.chat_manager.get_chat_list()

    # def get_chat_info(self, chat_id: int) -> Chat:
    #     return self.chat_manager.get_chat_info(chat_id)
    #
    # def send_text_message(self, chat_id: int, message: str) -> None:
    #     message = constants.string_to_bytes(message)
    #     message = constants.message_type_to_bytes(ChatMessageType.TEXT_MESSAGE) + message
    #     message = constants.id_to_bytes(chat_id) + message
    #     self.chat_manager.handle_message(message)
    #     # Then send all users this message
