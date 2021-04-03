from enum import IntEnum

PRIVATE_KEY_LENGTH: int = 16
ID_LENGTH: int = 16

BYTE_ORDER: str = "big"
REQUEST_TYPE_BYTE_SIZE: int = 1
MESSAGE_TYPE_BYTE_SIZE: int = 1
MESSAGE_LENGTH_BYTE_SIZE: int = 2
HMAC_BYTE_SIZE: int = 20

PORT_ID: int = 8080
MAX_CONNECTION_TRIES_COUNT: int = 14
WAITING_TIME_FOR_NEXT_CONNECTION: float = 0.313


def to_bytes(message_type: IntEnum) -> bytes:
    return int(message_type).to_bytes(MESSAGE_TYPE_BYTE_SIZE, BYTE_ORDER)


def to_int(message_type: bytes) -> int:
    return int.from_bytes(message_type, BYTE_ORDER)
