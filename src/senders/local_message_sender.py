from typing import Optional, Callable, Dict

from src.message_builders.message_builder import MessageBuilder
from src.senders.message_sender import MessageSender


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}

    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes]) -> None:
        super().__init__(ip, on_message_received, on_request_received)
        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, message: bytes) -> None:
        message = MessageBuilder.message() \
            .append_bytes(message) \
            .build_with_length()

        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        request = MessageBuilder.request() \
            .append_bytes(request) \
            .build_with_length()

        return self.message_senders[target_ip].handle_request(request)
