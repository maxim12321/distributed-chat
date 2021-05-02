import threading
from time import sleep
from typing import Optional, Callable, Dict, List, Tuple

from src.senders.message_sender import MessageSender


class LocalMessageSender(MessageSender):
    message_senders: Dict[bytes, 'LocalMessageSender'] = {}
    sockets: List[Tuple[bytes, bytes]] = []

    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes],
                 on_long_polling_request_received: Callable[[bytes], None]) -> None:
        super().__init__(ip, on_message_received, on_request_received, on_long_polling_request_received)

        self.lock = threading.Lock()
        self.long_polling_thread = threading.Thread(target=self.send_long_polling_requests)
        self.long_polling_thread.start()

        self.message_senders[ip] = self

    def send_message(self, target_ip: bytes, message: bytes) -> None:
        self.message_senders[target_ip].handle_message(message)

    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        return self.message_senders[target_ip].handle_request(request)

    def add_long_polling_request(self, target_ip: bytes, request: bytes) -> None:
        with self.lock:
            self.sockets.append((target_ip, request))

    def send_long_polling_requests(self):
        while True:
            for target_ip, message in self.sockets:
                answer = self.send_request(target_ip, message)
                self.on_long_polling_request_received(answer)
                sleep(5)

    def __del__(self):
        self.long_polling_thread.join()
