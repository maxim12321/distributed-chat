import os
import base64
from message_handler import MessageHandler
from chat_message_type import ChatMessageType
import constants


class Chat:
    def __init__(self, chat_name: str):
        self.message_handler = MessageHandler()
        self.private_key = None
        self.chat_name = chat_name
        self.chat_id = None

    def generate_private_key(self) -> None:
        self.private_key = os.urandom(constants.PRIVATE_KEY_LENGTH)

    def generate_invite_link(self, ip_address: bytes) -> str:
        link_bytes = base64.b64encode(self.private_key + ip_address)
        return link_bytes.decode("utf-8")

    def parse_invite_link(self, link: str) -> None:
        link_bytes = base64.b64decode(link)
        self.private_key = link_bytes[:constants.PRIVATE_KEY_LENGTH]

    def handle_message(self, message: bytes) -> bytes:
        message_type = ChatMessageType(constants.to_int(message[:constants.MESSAGE_TYPE_BYTE_SIZE]))
        message_content = message[constants.MESSAGE_TYPE_BYTE_SIZE:]
        if message_type == ChatMessageType.TEXT_MESSAGE:
            self.message_handler.handle_text_message(message_content)
            return bytearray()

        if message_type == ChatMessageType.INTRODUCE_USER:
            self.message_handler.handle_introduce_user(message_content)
            user_id_list_bytes = self.get_user_list_message()
            return user_id_list_bytes

        if message_type == ChatMessageType.USER_LIST:
            self.message_handler.handle_user_list(message_content)
            return bytearray()

    def get_user_list_message(self) -> bytes:
        user_id_list = self.message_handler.get_user_id_list()
        user_id_list_bytes = bytearray().join(user_id_list)
        return constants.to_bytes(ChatMessageType.USER_LIST) + user_id_list_bytes

    def get_introduce_user_message(self, user_id: bytes) -> bytes:
        return constants.to_bytes(ChatMessageType.INTRODUCE_USER) + user_id
