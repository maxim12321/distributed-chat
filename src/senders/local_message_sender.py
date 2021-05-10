from dataclasses import dataclass
from typing import Optional, Callable, Dict, List
from src.senders.message_sender import MessageSender
import threading


@dataclass
class RequestInfo:
    target_ip: bytes
    message: bytes
    sender_thread: Optional[threading.Thread]


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}

    def __init__(self, ip: bytes, port: int,
                 on_message_received: Callable[[bytes], Optional[bytes]],
                 on_request_received: Callable[[bytes], Optional[bytes]]) -> None:
        super().__init__(ip, port, on_message_received, on_request_received)

        self.requests: List[RequestInfo] = []

        self.answer: bytes = bytes()
        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, target_port: int, message: bytes) -> None:
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, target_port: int, request: bytes) -> Optional[bytes]:
        return self.message_senders[target_ip].handle_request(request)
