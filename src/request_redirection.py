from chat_message_type import ChatMessageType
from byte_message_type import ByteMessageType
import constants


class RequestRedirection:
    def __init__(self):
        self.handlers = dict((type, []) for type in ChatMessageType)

    def subscribe(self, type: ChatMessageType, handler: callable):
        self.handlers[type].append(handler)

    def handle(self, address: (str, int), message: bytes):
        type = ByteMessageType(constants.to_int(message[:constants.MESSAGE_TYPE_BYTE_SIZE]))
        message = message[constants.MESSAGE_TYPE_BYTE_SIZE:]
        try:
            for handler in self.handlers[type]:
                try:
                    return handler(message)
                except TypeError:
                    print(f"Function {handler.__name__} has wrong arguments")
        except KeyError:
            print(f"Wrong ByteMessageType. Got {type}")
            return
