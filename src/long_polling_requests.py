from src.senders.message_sender import MessageSender
from typing import List, Dict

import threading
import socket
import select


class LongPollingRequests:
    def __init__(self, on_request_received: callable):
        self.message_senders: Dict[socket, (MessageSender, bytes, bytes)] = {}
        self.receiving_thread = threading.Thread(target=self.receive)
        self.on_request_received = on_request_received
        self.receiving_thread.start()

    def add_request(self, target_ip: bytes, message_sender: MessageSender, request: bytes):
        current_socket = message_sender.send_request_message(target_ip, request)
        self.message_senders[current_socket] = (message_sender, target_ip, request)

    def receive(self):
        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.message_senders.keys(),
                                                                       self.message_senders.keys(),
                                                                       self.message_senders.keys())
            for current_socket in read_sockets:
                message_sender, target_ip, request = self.message_senders[current_socket]

                answer = message_sender.receive_message(current_socket)
                if answer is None:
                    continue
                self.on_request_received(answer)
                message_sender.send_request_message(target_ip, request)
