from typing import Dict, List, Callable, Optional

from chat_message_type import ChatMessageType
from byte_message_type import ByteMessageType
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
import constants
from enum import IntEnum


class MessageRedirection:
    def __init__(self):
        self.handlers: Dict[ByteMessageType, List[Callable[[bytes], Optional[bytes]]]] = {}

    def subscribe(self, byte_message_type: ByteMessageType, handler: Callable[[bytes], None]) -> None:
        if byte_message_type not in self.handlers:
            self.handlers[byte_message_type] = []
        self.handlers[byte_message_type].append(handler)

    def handle(self, message: bytes) -> None:
        byte_message_type: Container[ByteMessageType] = Container()

        message = MessageParser.parser(message) \
            .append_type(byte_message_type) \
            .parse()

        try:
            for handler in self.handlers[byte_message_type.get()]:
                handler(message)
        except KeyError:
            print(f"Wrong ByteMessageType. Got {byte_message_type}")
            return
