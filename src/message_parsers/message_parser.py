import json
from enum import IntEnum
from typing import Generic, Optional, TypeVar, List, Type

from src import constants, json_decoder
from src.chat_message_cipher import ChatMessageCipher
from src.message_parsers.container import Container
from src.security.authentication import Authentication
from src.serializable import Serializable


class AuthenticationError(Exception):
    pass


class MessageParser:
    def __init__(self, data: bytes, parent: Optional['MessageParser'] = None) -> None:
        self.parent: Optional[MessageParser] = parent
        self.data: bytes = data

    def append_type(self, value: Container[IntEnum]) -> 'MessageParser':
        value.set(self._pop_int(constants.TYPE_BYTE_SIZE))
        return self

    def append_id(self, value: Container[int]) -> 'MessageParser':
        value.set(self._pop_int(constants.ID_LENGTH))
        return self

    def append_bytes(self, value: Container[bytes]) -> 'MessageParser':
        length = self._pop_int(constants.MESSAGE_LENGTH_BYTE_SIZE)
        value.set(self._pop_bytes(length))
        return self

    def append_string(self, value: Container[str]) -> 'MessageParser':
        data: Container[bytes] = Container()
        self.append_bytes(data)
        value.set(data.get().decode("utf-8"))
        return self

    def append_object(self, value: Container[object]) -> 'MessageParser':
        data: Container[str] = Container()
        self.append_string(data)

        value.set(json.loads(data.get(), object_hook=json_decoder.decode))
        return self

    def append_serializable(self, value: Serializable) -> 'MessageParser':
        data: Container[dict] = Container()
        self.append_object(data)
        value.load_from_dict(data.get())
        return self

    def append_serializable_list(self, values: Container[List[Serializable]],
                                 serializable_type: Type[Serializable]) -> 'MessageParser':
        value_dicts: Container[List[dict]] = Container()
        self.append_object(value_dicts)

        parsed_values: List[Serializable] = []
        for value_dict in value_dicts.get():
            value = serializable_type()
            value.load_from_dict(value_dict)
            parsed_values.append(value)

        values.set(parsed_values)
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

        self.data = Authentication.authenticate(self.data, key)
        if self.data is None:
            raise AuthenticationError

    def authenticate(self) -> T:
        if self.parent is None:
            self.parent = self.parser(self.data)
        return self.parent


class EncryptedParser(MessageParser, Generic[T]):
    def __init__(self, data: bytes, key: bytes, parent: Optional[T] = None) -> None:
        super().__init__(data, parent)

        cipher = ChatMessageCipher(key)
        self.data = cipher.decrypt_data(data)

    def encrypt(self) -> T:
        if self.parent is None:
            self.parent = self.parser(self.data)
        return self.parent
