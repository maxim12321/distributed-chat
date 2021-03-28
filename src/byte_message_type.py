from enum import IntEnum


class ByteMessageType(IntEnum):
    TEXT_MESSAGE = 1
    INTRODUCE_USER = 2
    USER_LIST = 3
