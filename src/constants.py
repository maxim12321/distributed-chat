import base64
from enum import IntEnum
import os

PRIVATE_KEY_LENGTH: int = 16
ID_LENGTH: int = 16

BYTE_ORDER: str = "big"
REQUEST_TYPE_BYTE_SIZE: int = 1
MESSAGE_TYPE_BYTE_SIZE: int = 1
MESSAGE_LENGTH_BYTE_SIZE: int = 2
HMAC_BYTE_SIZE: int = 20
BLOCK_SIZE: int = 32

PORT_ID: int = 8080
MAX_CONNECTION_TRIES_COUNT: int = 14
WAITING_TIME_FOR_NEXT_CONNECTION: float = 0.313

INDENT: int = 4


def message_type_to_bytes(message_type: IntEnum) -> bytes:
    return int(message_type).to_bytes(MESSAGE_TYPE_BYTE_SIZE, BYTE_ORDER)


def message_length_to_bytes(length: int) -> bytes:
    return length.to_bytes(MESSAGE_LENGTH_BYTE_SIZE, BYTE_ORDER)


def request_type_to_bytes(request_type: IntEnum) -> bytes:
    return int(request_type).to_bytes(REQUEST_TYPE_BYTE_SIZE, BYTE_ORDER)


def id_to_bytes(object_id: int) -> bytes:
    return object_id.to_bytes(ID_LENGTH, BYTE_ORDER)


def to_int(message_type: bytes) -> int:
    return int.from_bytes(message_type, BYTE_ORDER)


def random_int(bytes_count: int) -> int:
    return int.from_bytes(os.urandom(bytes_count), BYTE_ORDER)


def bytes_to_string(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def string_to_bytes(data: bytes) -> bytes:
    return base64.b64decode(data)


def bytes_to_dict(data: bytes):
    return {"__bytes__": True, "bytes": bytes_to_string(data)}
