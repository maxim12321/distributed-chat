from typing import Callable, Dict, List, Optional

from src.byte_message_type import ByteMessageType
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser


class MessageRedirection:

    def __init__(self):
        self.handlers: Dict[ByteMessageType, List[Callable[[bytes], Optional[bytes]]]] \
            = dict((byte_message_type, []) for byte_message_type in ByteMessageType)

    def subscribe(self, byte_message_type: ByteMessageType, handler: Callable[[bytes], Optional[bytes]]) -> None:
        self.handlers[byte_message_type].append(handler)

    def handle(self, message: bytes) -> Optional[bytes]:
        byte_message_type: Container[ByteMessageType] = Container()

        message = MessageParser.parser(message) \
            .append_type(byte_message_type) \
            .parse()

        for handler in self.handlers[byte_message_type.get()]:
            return handler(message)
