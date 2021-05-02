import socket
import threading
from typing import Callable, Optional

from src import constants
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.senders.message_sender import MessageSender
from src.senders.message_type import MessageType


class SocketMessageSender(MessageSender):
    def __init__(self, ip: bytes,
                 on_message_received: Callable[[bytes], None],
                 on_request_received: Callable[[bytes], bytes]) -> None:
        super().__init__(ip, on_message_received, on_request_received)

        self.ip = ip

        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listen)
        self.listening_thread.start()

    def send_message(self, target_ip: bytes, message: bytes) -> None:
        sending_socket = self._connect(target_ip)
        if sending_socket is None:
            return

        message = MessageBuilder.message() \
            .append_bytes(message) \
            .build_with_length()

        sending_socket.send(message)

    def send_request(self, target_ip: bytes, request: bytes) -> Optional[bytes]:
        sending_socket = self._connect(target_ip)
        if sending_socket is None:
            return None

        request = MessageBuilder.request() \
            .append_bytes(request) \
            .build_with_length()

        sending_socket.send(request)
        return self._receive_message(sending_socket)

    @staticmethod
    def _connect(target_ip: bytes) -> Optional[socket]:
        destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for _ in range(constants.MAX_CONNECTION_TRIES_COUNT):
            try:
                destination_socket.connect((target_ip, constants.PORT_ID))
                return destination_socket
            except ConnectionRefusedError:
                continue

        return None

    def _listen(self) -> None:
        listening_socket = self._create_socket(constants.LISTENING_TIMEOUT)

        while self.is_listening:
            try:
                message_socket, address = listening_socket.accept()

                message = self._receive_message(message_socket)
                self._process_message(message, message_socket)

            except socket.timeout:
                pass

    def _create_socket(self, timeout: float) -> socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, constants.PORT_ID))
        sock.listen(1)
        sock.settimeout(timeout)
        return sock

    @staticmethod
    def _receive_message(message_socket: socket) -> Optional[bytes]:
        message_socket.settimeout(constants.MESSAGE_TIMEOUT)

        try:
            message_length = constants.to_int(message_socket.recv(constants.MESSAGE_LENGTH_BYTE_SIZE))

            if message_length == 0:
                message_socket.close()
                return None
            return message_socket.recv(message_length)

        except socket.timeout:
            return None

    def _process_message(self, message: bytes, message_socket: socket) -> None:
        message_type = Container[MessageType]()
        message = MessageParser.parser(message) \
            .append_type(message_type) \
            .parse()

        if message_type.get() == MessageType.MESSAGE:
            self.handle_message(message)
        elif message_type.get() == MessageType.REQUEST:
            answer = MessageBuilder.builder() \
                    .append_bytes(self.handle_request(message)) \
                    .build_with_length()
            message_socket.send(answer)

    def __del__(self) -> None:
        self.is_listening = False
        self.listening_thread.join()