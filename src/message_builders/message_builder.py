import json
from enum import IntEnum
from typing import Generic, Optional, TypeVar

from src import constants
from src.byte_message_socket import ByteMessageSocket, MessageType
from src.chat_message_cipher import ChatMessageCipher


class MessageBuilder:
    def __init__(self, parent: Optional['MessageBuilder'] = None) -> None:
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

    def append_serializable(self, value: object) -> 'MessageBuilder':
        data = json.dumps(value).encode("utf-8")
        self.append_bytes(data)
        return self

    def begin_authenticated(self) -> 'AuthenticatedBuilder':
        return AuthenticatedBuilder(parent=self)

    def begin_encrypted(self) -> 'EncryptedBuilder':
        return EncryptedBuilder(parent=self)

    def build(self) -> bytes:
        return bytes(self.data)

    @staticmethod
    def message() -> 'MessageBuilder':
        builder = MessageBuilder()
        builder.append_type(MessageType.MESSAGE)
        return builder

    @staticmethod
    def request() -> 'MessageBuilder':
        builder = MessageBuilder()
        builder.append_type(MessageType.REQUEST)
        return builder


T = TypeVar('T')


class AuthenticatedBuilder(MessageBuilder, Generic[T]):
    def authenticate(self, key: bytes) -> T:
        if self.parent is None:
            self.parent = MessageBuilder()

        authenticated_data = ByteMessageSocket.add_authentication_code(bytes(self.data), key)

        self.parent.append_bytes(authenticated_data)
        return self.parent


class EncryptedBuilder(MessageBuilder, Generic[T]):
    def encrypt(self, key: bytes) -> T:
        if self.parent is None:
            self.parent = MessageBuilder()

        cipher = ChatMessageCipher(key)
        encrypted_data = cipher.encrypt_data(bytes(self.data))

        self.parent.append_bytes(encrypted_data)
        return self.parent
