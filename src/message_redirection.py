from src.byte_message_type import ByteMessageType


class MessageRedirection:
    def __init__(self):
        self.BYTE_ORDER = "big"
        self.list_of_handlers = {}
        for type in ByteMessageType:
            self.list_of_handlers[type] = []

    def subscribe(self, type: ByteMessageType, handler: callable) -> None:
        self.list_of_handlers[type].append(handler)

    def handle(self, address, message: bytes) -> None:
        type = int.from_bytes(message[0:1], self.BYTE_ORDER)
        message = message[1:]
        try:
            for handler in self.list_of_handlers[type]:
                handler(message)
        except KeyError:
            return
