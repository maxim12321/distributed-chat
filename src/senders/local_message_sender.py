import signal
import threading
import random
from time import sleep
from typing import Optional, Callable, Dict, List, Tuple
from src.senders.message_sender import MessageSender


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}

    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes],
                 on_long_polling_response_received: Callable[[bytes], None]) -> None:
        super().__init__(ip, on_message_received, on_request_received, on_long_polling_response_received)

        self.requests: List = []
        self.answers: Dict[threading.Thread, bytes] = {}

        self.long_polling_thread = threading.Thread(target=self.send_long_polling_requests)
        self.long_polling_thread.start()

        self.answer: bytes = bytes()
        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, message: bytes) -> None:
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        answer = self.message_senders[target_ip].handle_request(request)
        self.answers[threading.current_thread()] = answer
        return answer

    def add_long_polling_request(self, target_ip: bytes, request: bytes) -> None:
        self.requests.append([target_ip, request, None])

    def send_long_polling_requests(self) -> None:
        while True:
            for ind, info in enumerate(self.requests):
                target_ip, message, sender_thread = info
                if sender_thread is None:
                    self.requests[ind][2] = threading.Thread(target=self.send_request, args=(target_ip, message))
                    self.requests[ind][2].start()
                self.requests[ind][2].join(3)
                if self.requests[ind][2].is_alive():
                    continue

                self.on_long_polling_response_received(self.answers[self.requests[ind][2]])
                self.requests[ind][2] = None

    def __del__(self) -> None:
        self.long_polling_thread.join()
