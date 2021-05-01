from abc import ABC, abstractmethod
from typing import Callable, Optional

from src.byte_message_type import ByteMessageType


class MessageSender(ABC):
    @abstractmethod
    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes]) -> None:
        self.on_message_received = on_message_received
        self.on_request_received = on_request_received

    @abstractmethod
    def send_message(self, target_ip: bytes, message_type: ByteMessageType, message: bytes) -> None:
        pass

    @abstractmethod
    def send_request(self, target_ip: bytes, message_type: ByteMessageType, request: bytes) -> Optional[bytes]:
        pass

    def handle_message(self, message: bytes) -> None:
        self.on_message_received(message)

    def handle_request(self, request: bytes) -> bytes:
        return self.on_request_received(request)
