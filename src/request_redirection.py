from enum import IntEnum

from byte_message_type import ByteMessageType
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser


class RequestRedirection:
    def __init__(self):
        self.handlers = dict((type, []) for type in ByteMessageType)

    def subscribe(self, type: ByteMessageType, handler: callable):
        self.handlers[type].append(handler)

    def handle(self, message: bytes):
        type = Container[IntEnum]()

        message = MessageParser.parser(message) \
            .append_type(type) \
            .parse()

        try:
            for handler in self.handlers[type.get()]:
                try:
                    return handler(message)
                except TypeError:
                    print(f"Function {handler.__name__} has wrong arguments")
        except KeyError:
            print(f"Wrong ByteMessageType. Got {type}")
            return
