from typing import Optional, Callable, Dict

from src.senders.message_sender import MessageSender


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}

    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes]) -> None:
        super().__init__(ip, on_message_received, on_request_received)
        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, message: bytes) -> None:
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        return self.message_senders[target_ip].handle_request(request)
