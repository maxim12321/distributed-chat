from enum import IntEnum


class ChatMessageType(IntEnum):
    TEXT_MESSAGE = 1
    INTRODUCE_USER = 2
    USER_LIST = 3
    IMAGE = 4
    IMAGE_ID = 5
