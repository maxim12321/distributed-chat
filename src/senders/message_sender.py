from abc import ABC, abstractmethod
from typing import Callable, Optional


class MessageSender(ABC):
    @abstractmethod
    def __init__(self, ip: bytes, port: int,
                 on_message_received: Callable[[bytes], Optional[bytes]],
                 on_request_received: Callable[[bytes], Optional[bytes]]) -> None:
        self.ip = ip
        self.port = port
        self.on_message_received = on_message_received
        self.on_request_received = on_request_received

    @abstractmethod
    def send_message(self, target_ip: bytes, target_port: int, message: bytes) -> None:
        pass

    @abstractmethod
    def send_request(self, target_ip: bytes, target_port: int, request: bytes) -> Optional[bytes]:
        pass

    def handle_message(self, message: bytes) -> None:
        self.on_message_received(message)

    def handle_request(self, request: bytes) -> bytes:
        return self.on_request_received(request)

    def __del__(self):
        pass
