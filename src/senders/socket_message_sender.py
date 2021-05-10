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
    def __init__(self, ip: bytes, port: int,
                 on_message_received: Callable[[bytes], Optional[bytes]],
                 on_request_received: Callable[[bytes], Optional[bytes]]) -> None:
        super().__init__(ip, port, on_message_received, on_request_received)

        self.is_listening = True
        self.on_long_poll_received: Optional[Callable[[socket.socket, bytes], None]] = None

        self.listening_thread = threading.Thread(target=self._listen)
        self.listening_thread.start()

    def send_message(self, target_ip: bytes, target_port: int, message: bytes) -> bool:
        sending_socket = self._connect(target_ip, target_port)
        if sending_socket is None:
            return False
        try:
            message = MessageBuilder.message() \
                .append_bytes(message) \
                .build_with_length()

            sending_socket.send(message)
            return True
        except ConnectionRefusedError:
            return False

    def send_request(self, target_ip: bytes, target_port: int, request: bytes) -> Optional[bytes]:
        sending_socket = self._connect(target_ip, target_port)
        if sending_socket is None:
            return None

        request = MessageBuilder.request() \
            .append_bytes(request) \
            .build_with_length()
        try:
            sending_socket.send(request)
        except ConnectionError:
            return None

        answer = self.receive_message(sending_socket)
        if answer is None:
            return None

        response: Container[bytes] = Container()
        MessageParser.parser(answer) \
            .append_bytes(response) \
            .parse()
        return response.get()

    def send_long_polling_message(self, target_ip: bytes, target_port: int,
                                  message: bytes, long_polling_id: int) -> Optional[socket.socket]:
        sending_socket = self._connect(target_ip, target_port)
        if sending_socket is None:
            return None
        try:
            message = MessageBuilder.long_polling_request() \
                .append_id(long_polling_id) \
                .append_bytes(message) \
                .build_with_length()

            sending_socket.send(message)
            return sending_socket
        except ConnectionError:
            return None

    def set_long_polling_callback(self, on_long_polling_received: Callable[[socket.socket, bytes], None]) -> None:
        self.on_long_poll_received = on_long_polling_received

    @staticmethod
    def _connect(target_ip: bytes, target_port: int) -> Optional[socket.socket]:
        destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        for _ in range(constants.MAX_CONNECTION_TRIES_COUNT):
            try:
                destination_socket.connect((socket.inet_ntoa(target_ip), target_port))
                return destination_socket
            except ConnectionError:
                continue

        return None

    @staticmethod
    def receive_message(message_socket: socket) -> Optional[bytes]:
        message_socket.settimeout(constants.MESSAGE_TIMEOUT)

        try:
            message_length = constants.to_int(message_socket.recv(constants.MESSAGE_LENGTH_BYTE_SIZE))
            if message_length == 0:
                message_socket.close()

                return None
            return message_socket.recv(message_length)

        except ConnectionError:
            return None

    def _listen(self) -> None:
        listening_socket = self._create_socket(constants.LISTENING_TIMEOUT)

        while self.is_listening:
            try:
                message_socket, address = listening_socket.accept()

                message = self.receive_message(message_socket)
                if message is None:
                    continue

                self._process_message(message, message_socket)

            except socket.timeout:
                pass

    def _create_socket(self, timeout: float) -> socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((socket.inet_ntoa(self.ip), self.port))
        sock.listen(1)
        sock.settimeout(timeout)
        return sock

    def _process_message(self, message: bytes, message_socket: socket) -> None:
        message_type = Container[MessageType]()
        message_context = Container[bytes]()
        message = MessageParser.parser(message) \
            .append_type(message_type) \
            .parse()

        if message_type.get() == MessageType.LONG_POLLING_REQUEST:
            self.on_long_poll_received(message_socket, message)
            return

        MessageParser.parser(message) \
            .append_bytes(message_context) \
            .parse()
        if message_type.get() == MessageType.MESSAGE:
            self.handle_message(message_context.get())
            return

        if message_type.get() == MessageType.REQUEST:
            try:
                answer = MessageBuilder.builder() \
                    .append_bytes(self.handle_request(message_context.get())) \
                    .build_with_length()
                message_socket.send(answer)
            except ConnectionError:
                pass

    def __del__(self) -> None:
        self.is_listening = False
        self.listening_thread.join()
