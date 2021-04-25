import json
from enum import IntEnum
from typing import Generic, Optional, TypeVar

from src import constants
from src.byte_message_socket import ByteMessageSocket
from src.chat_message_cipher import ChatMessageCipher
from src.message_parsers.container import Container


class AuthenticationError(Exception):
    pass


class MessageParser:
    def __init__(self, data: bytes, parent: Optional['MessageParser'] = None) -> None:
        self.parent: Optional[MessageParser] = parent
        self.data: bytes = data

    def append_type(self, value: Container[IntEnum]) -> 'MessageParser':
        type_value = self._pop_int(constants.TYPE_BYTE_SIZE)
        value.set(type_value)
        return self

    def append_id(self, value: Container[int]) -> 'MessageParser':
        value.set(self._pop_int(constants.ID_LENGTH))
        return self

    def append_bytes(self, value: Container[bytes]) -> 'MessageParser':
        length = self._pop_int(constants.MESSAGE_LENGTH_BYTE_SIZE)
        value.set(self._pop_bytes(length))
        return self

    def append_serializable(self, value: Container[object]) -> 'MessageParser':
        length = self._pop_int(constants.MESSAGE_LENGTH_BYTE_SIZE)
        data = self._pop_bytes(length)
        value.set(json.loads(data.decode("utf-8")))
        return self

    def begin_authenticated(self, key: bytes) -> 'AuthenticatedParser':
        length = self._pop_int(constants.MESSAGE_LENGTH_BYTE_SIZE)
        authenticated_bytes = self._pop_bytes(length)
        return AuthenticatedParser(authenticated_bytes, key, parent=self)

    def begin_encrypted(self, key: bytes) -> 'EncryptedParser':
        length = self._pop_int(constants.MESSAGE_LENGTH_BYTE_SIZE)
        encrypted_bytes = self._pop_bytes(length)
        return EncryptedParser(encrypted_bytes, key, parent=self)

    def parse(self) -> bytes:
        return bytes(self.data)

    def _pop_bytes(self, length: int) -> bytes:
        data_bytes = self.data[:length]
        self.data = self.data[length:]
        return data_bytes

    def _pop_int(self, length: int) -> int:
        int_bytes = self._pop_bytes(length)
        return constants.to_int(int_bytes)

    @staticmethod
    def parser(data: bytes) -> 'MessageParser':
        return MessageParser(data)


T = TypeVar('T')


class AuthenticatedParser(MessageParser, Generic[T]):
    def __init__(self, data: bytes, key: bytes, parent: Optional[T] = None) -> None:
        super().__init__(data, parent)

        self.data = ByteMessageSocket.authenticate(self.data, key)
        if self.data is None:
            raise AuthenticationError

    def authenticate(self) -> T:
        if self.parent is None:
            self.parent = MessageParser(self.data)
        return self.parent


class EncryptedParser(MessageParser, Generic[T]):
    def __init__(self, data: bytes, key: bytes, parent: Optional[T] = None) -> None:
        super().__init__(data, parent)

        cipher = ChatMessageCipher(key)
        self.data = cipher.decrypt_data(data)

    def encrypt(self) -> T:
        if self.parent is None:
            self.parent = MessageParser(self.data)
        return self.parent
