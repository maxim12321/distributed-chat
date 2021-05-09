from dataclasses import dataclass
from typing import Optional, Callable, Dict, List, Tuple
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
                 on_request_received: Callable[[bytes], Optional[bytes]],
                 on_long_polling_response_received: Callable[[bytes], Optional[bytes]]) -> None:
        super().__init__(ip, port, on_message_received, on_request_received, on_long_polling_response_received)

        self.requests: List[RequestInfo] = []
        self.answers: Dict[threading.Thread, bytes] = {}
        self.is_listening = True

        self.long_polling_thread = threading.Thread(target=self._send_long_polling_requests)
        self.long_polling_thread.start()

        self.answer: bytes = bytes()
        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, target_port: int, message: bytes) -> None:
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, target_port: int, request: bytes) -> Optional[bytes]:
        answer = self.message_senders[target_ip].handle_request(request)
        self.answers[threading.current_thread()] = answer
        return answer

    def add_long_polling_request(self, target_ip: bytes, target_port: int, request: bytes) -> None:
        self.requests.append(RequestInfo(target_ip, request, None))

    def _send_long_polling_requests(self) -> None:
        while self.is_listening:
            # print(self.is_listening)
            for index, request_info in enumerate(self.requests):
                if request_info.sender_thread is None:
                    self.requests[index].sender_thread = threading.Thread(target=self.send_request,
                                                                          args=(request_info.target_ip,
                                                                                request_info.message))
                    self.requests[index].sender_thread.start()

                if self.requests[index].sender_thread.is_alive():
                    continue

                self.on_long_polling_response_received(self.answers[self.requests[index].sender_thread])
                self.requests[index].sender_thread = None

    def __del__(self) -> None:
        self.is_listening = False
        self.long_polling_thread.join()
