from enum import IntEnum


class ChatMessageType(IntEnum):
    SET_CHAT_NAME = 0
    TEXT_MESSAGE = 1
    INTRODUCE_USER = 2
    GET_CHAT = 3
    IMAGE_MESSAGE = 4
    IMAGE_REQUEST = 5
