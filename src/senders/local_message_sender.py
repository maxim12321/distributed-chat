from typing import Optional, Callable, Dict

from src.senders.message_sender import MessageSender
import socket


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}
    sockets: Dict[int, bytes] = {}
    id: int = 0

    def __init__(self, ip: bytes, current_socket: int,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes]) -> None:
        super().__init__(ip, on_message_received, on_request_received)
        self.message_senders[ip] = self
        self.current_socket = current_socket

    def send_message(self, target_ip: bytes, message: bytes) -> None:
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        return self.message_senders[target_ip].handle_request(request)

    def send_request_message(self, target_ip: bytes, message: bytes):
        self.sockets[self.current_socket] = self.send_request(target_ip, message)
        return self.current_socket

    def receive_message(self, current_socket) -> Optional[bytes]:
        return self.sockets[current_socket]
