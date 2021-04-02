import os
import base64
from message_handler import MessageHandler
from byte_message_type import ByteMessageType


class Chat:
    def __init__(self, chat_name: str):
        self.PRIVATE_KEY_LENGTH = 16
        self.BYTE_ORDER = "big"
        self.MESSAGE_TYPE_BYTE_SIZE = 1

        self.message_handler = MessageHandler()
        self.user_id_list = []
        self.message_list = []

        self.private_key = None
        self.chat_name = chat_name
        self.chat_id = None

    def generate_private_key(self) -> None:
        self.private_key = os.urandom(self.PRIVATE_KEY_LENGTH)

    def generate_invite_link(self, ip_address: bytes) -> str:
        link_bytes = base64.b64encode(self.private_key + ip_address)
        return link_bytes.decode("utf-8")

    def parse_invite_link(self, link: str) -> None:
        link_bytes = base64.b64decode(link)
        self.private_key = link_bytes[:self.PRIVATE_KEY_LENGTH]

    def handle_message(self, message: bytes) -> bytes:
        message_type = int.from_bytes(message[:1], self.BYTE_ORDER)
        if message_type == 0x01:
            self.message_handler.handle_text_message(message[1:], self.message_list)
            return bytearray()
        elif message_type == 0x02:
            self.message_handler.handle_introduce_user(message[1:], self.user_id_list)
            user_id_list_bytes = self.get_user_list_message()
            return user_id_list_bytes
        else:
            self.message_handler.handle_user_list(message[1:], self.user_id_list)
            return bytearray()

    def get_user_list_message(self) -> bytes:
        user_id_list_bytes = bytearray()
        for id in self.user_id_list:
            user_id_list_bytes += id
        return int(ByteMessageType.USER_LIST).to_bytes(self.MESSAGE_TYPE_BYTE_SIZE,
                                                       self.BYTE_ORDER) + user_id_list_bytes

    def get_introduce_user_message(self, user_id: bytes) -> bytes:
        return int(ByteMessageType.INTRODUCE_USER).to_bytes(self.MESSAGE_TYPE_BYTE_SIZE,
                                                            self.BYTE_ORDER) + user_id
