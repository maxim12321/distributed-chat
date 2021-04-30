from typing import Optional, Callable, Dict

from src import constants
from src.byte_message_type import ByteMessageType
from src.senders.message_sender import MessageSender
from src.senders.message_type import MessageType


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}

    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes]) -> None:
        super().__init__(ip, on_message_received, on_request_received)
        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, message_type: ByteMessageType, message: bytes) -> None:
        message = self._finalize_message(MessageType.MESSAGE, message_type, message)
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, message_type: ByteMessageType, request: bytes) -> Optional[bytes]:
        request = self._finalize_message(MessageType.REQUEST, message_type, request)
        return self.message_senders[target_ip].handler_request(request)

    @staticmethod
    def _finalize_message(message_type: MessageType, byte_message_type: ByteMessageType, message: bytes) -> bytes:
        message = constants.message_type_to_bytes(byte_message_type) + message
        message = constants.request_type_to_bytes(message_type) + message
        message = constants.message_length_to_bytes(len(message)) + message
        return message
