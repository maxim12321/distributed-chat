from enum import IntEnum

from chat_message_type import ChatMessageType
from byte_message_type import ByteMessageType

PRIVATE_KEY_LENGTH: int = 16
ID_LENGTH: int = 16

BYTE_ORDER: str = "big"
MESSAGE_TYPE_BYTE_SIZE: int = 1
MESSAGE_LENGTH_BYTE_SIZE: int = 2
HMAC_BYTE_SIZE: int = 20

PORT_ID: int = 8080
MAX_CONNECTION_TRIES_COUNT: int = 14
WAITING_TIME_FOR_NEXT_CONNECTION: float = 0.313


def to_bytes(message_type: IntEnum) -> bytes:
    return int(message_type).to_bytes(MESSAGE_TYPE_BYTE_SIZE, BYTE_ORDER)


def to_chat_message_type(message_type: bytes) -> ChatMessageType:
    type_int = int.from_bytes(message_type, BYTE_ORDER)
    if type_int == 1:
        return ChatMessageType.TEXT_MESSAGE
    if type_int == 2:
        return ChatMessageType.INTRODUCE_USER
    if type_int == 3:
        return ChatMessageType.USER_LIST


def to_byte_message_type(message_type: bytes) -> ByteMessageType:
    type_int = int.from_bytes(message_type, BYTE_ORDER)
    if type_int == 1:
        return ByteMessageType.CHAT_MESSAGE
    if type_int == 2:
        return ByteMessageType.DHT_MESSAGE
