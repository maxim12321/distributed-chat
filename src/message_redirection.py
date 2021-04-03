from src.chat_message_type import ChatMessageType
import constants


class MessageRedirection:
    def __init__(self):
        self.handlers = dict((type, []) for type in ChatMessageType)

    def subscribe(self, type: ChatMessageType, handler: callable) -> None:
        self.handlers[type].append(handler)

    def handle(self, address: (str, int), message: bytes) -> None:
        type = constants.to_byte_message_type(message[:constants.MESSAGE_TYPE_BYTE_SIZE])
        message = message[constants.MESSAGE_TYPE_BYTE_SIZE:]
        try:
            for handler in self.handlers[type]:
                try:
                    handler(address, message)
                except TypeError:
                    print(f"Function {handler.__name__} has wrong arguments")
        except KeyError:
            print(f"Wrong ByteMessageType. Got {type}")
            return
