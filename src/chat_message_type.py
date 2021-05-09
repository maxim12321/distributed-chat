from enum import IntEnum


class ChatMessageType(IntEnum):
    TEXT_MESSAGE = 1
    INTRODUCE_USER = 2
    GET_CHAT = 3
    IMAGE = 4
    IMAGE_ID = 5
