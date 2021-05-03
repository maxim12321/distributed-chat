from abc import ABC, abstractmethod
from typing import Callable, Optional


class MessageSender(ABC):
    @abstractmethod
    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes],
                 on_long_polling_response_received: Callable[[bytes], None]) -> None:
        self.ip = ip
        self.on_message_received = on_message_received
        self.on_request_received = on_request_received
        self.on_long_polling_response_received = on_long_polling_response_received

    @abstractmethod
    def send_message(self, target_ip: bytes, message: bytes) -> None:
        pass

    @abstractmethod
    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        pass

    @abstractmethod
    def add_long_polling_request(self, target_ip: bytes, request: bytes) -> None:
        pass

    def handle_message(self, message: bytes) -> None:
        self.on_message_received(message)

    def handle_request(self, request: bytes) -> bytes:
        return self.on_request_received(request)

    def handle_long_polling_request(self, message: bytes):
        self.on_long_polling_response_received(message)
