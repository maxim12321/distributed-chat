from src.byte_message_type import ByteMessageType


class MessageRedirection:
    def __init__(self):
        self.BYTE_ORDER = "big"
        self.handlers = dict((type, []) for type in ByteMessageType)

    def subscribe(self, type: ByteMessageType, handler: callable) -> None:
        self.handlers[type].append(handler)

    def handle(self, address: (str, int), message: bytes) -> None:
        type = int.from_bytes(message[0:1], self.BYTE_ORDER)
        message = message[1:]
        try:
            for handler in self.handlers[type]:
                try:
                    handler(address, message)
                except TypeError:
                    print(f"Function {handler.__name__} has wrong arguments")
        except KeyError:
            print(f"Wrong ByteMessageType. Got {type}")
            return
