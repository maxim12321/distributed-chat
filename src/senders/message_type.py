from enum import IntEnum


class MessageType(IntEnum):
    REQUEST = 0
    MESSAGE = 1
    LONG_POLLING_REQUEST = 2
