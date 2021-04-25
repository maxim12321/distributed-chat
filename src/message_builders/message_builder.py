from enum import IntEnum
from typing import Generic, Optional, TypeVar

from src import constants
from src.byte_message_socket import ByteMessageSocket, MessageType
from src.chat_message_cipher import ChatMessageCipher


class MessageBuilder:
    def __init__(self, message_type: MessageType, parent: Optional['MessageBuilder'] = None) -> None:
        self.message_type = message_type
        self.parent: Optional[MessageBuilder] = parent
        self.data = bytearray()

    def append_type(self, value: IntEnum) -> 'MessageBuilder':
        self.data.extend(constants.type_to_bytes(value))
        return self

    def append_id(self, value: int) -> 'MessageBuilder':
        self.data.extend(constants.id_to_bytes(value))
        return self

    def append_bytes(self, value: bytes) -> 'MessageBuilder':
        self.data.extend(constants.message_length_to_bytes(len(value)))
        self.data.extend(value)
        return self

    def begin_authenticated(self) -> 'AuthenticatedBuilder':
        return AuthenticatedBuilder(self.message_type, parent=self)

    def begin_encrypted(self) -> 'EncryptedBuilder':
        return EncryptedBuilder(self.message_type, parent=self)

    def build(self) -> bytes:
        return constants.type_to_bytes(self.message_type) + bytes(self.data)

    @staticmethod
    def message() -> 'MessageBuilder':
        return MessageBuilder(MessageType.MESSAGE)

    @staticmethod
    def request() -> 'MessageBuilder':
        return MessageBuilder(MessageType.REQUEST)


T = TypeVar('T')


class AuthenticatedBuilder(MessageBuilder, Generic[T]):
    def authenticate(self, key: bytes) -> T:
        if self.parent is None:
            self.parent = MessageBuilder(self.message_type)

        authenticated_data = ByteMessageSocket.add_authentication_code(bytes(self.data), key)

        self.parent.append_bytes(authenticated_data)
        return self.parent


class EncryptedBuilder(MessageBuilder, Generic[T]):
    def encrypt(self, key: bytes) -> T:
        if self.parent is None:
            self.parent = MessageBuilder(self.message_type)

        cipher = ChatMessageCipher(key)
        encrypted_data = cipher.encrypt_data(bytes(self.data))

        self.parent.append_bytes(encrypted_data)
        return self.parent
