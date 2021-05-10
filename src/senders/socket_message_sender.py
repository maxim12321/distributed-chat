import select
import socket
import threading
from typing import Callable, Optional, Dict, Tuple

from src import constants
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.senders.message_sender import MessageSender
from src.senders.message_type import MessageType


class SocketMessageSender(MessageSender):
    def __init__(self, ip: bytes, port: int,
                 on_message_received: Callable[[bytes], Optional[bytes]],
                 on_request_received: Callable[[bytes], Optional[bytes]],
                 on_long_polling_response_received: Callable[[bytes], Optional[bytes]]) -> None:
        super().__init__(ip, port, on_message_received, on_request_received, on_long_polling_response_received)

        self.is_listening = True

        self.long_polling_sockets: Dict[socket, Tuple[bytes, int, bytes]] = {}
        self.long_polling_thread = threading.Thread(target=self._long_polling_requests)
        self.long_polling_thread.start()

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
        except ConnectionError:
            return False

    def send_request(self, target_ip: bytes, target_port: int, request: bytes) -> Optional[bytes]:
        sending_socket = self._send_request_message(target_ip, target_port, request)
        if sending_socket is None:
            return None

        answer = self._receive_message(sending_socket)
        if answer is None:
            return None

        response: Container[bytes] = Container()
        MessageParser.parser(answer) \
            .append_bytes(response) \
            .parse()

        return response.get()

    def add_long_polling_request(self, target_ip: bytes, target_port: int, request: bytes) -> None:
        current_socket = self._send_request_message(target_ip, target_port, request)
        if current_socket is None:
            return
        self.long_polling_sockets[current_socket] = (target_ip, target_port, request)

    def _send_request_message(self, target_ip: bytes, target_port: int, request: bytes) -> Optional[socket.socket]:
        sending_socket = self._connect(target_ip, target_port)
        if sending_socket is None:
            return None
        try:
            request = MessageBuilder.request() \
                .append_bytes(request) \
                .build_with_length()

            sending_socket.send(request)
            return sending_socket
        except ConnectionError:
            return None

    def _long_polling_requests(self) -> None:
        while self.is_listening:
            read_sockets = []
            if len(self.long_polling_sockets.keys()) != 0:
                read_sockets = select.select(self.long_polling_sockets.keys(), [], [])[0]

            for current_socket in read_sockets:
                target_ip, target_port, request = self.long_polling_sockets[current_socket]

                answer = self._receive_message(current_socket)
                if answer is None:
                    continue

                self.on_long_polling_response_received(answer)

                self.long_polling_sockets.pop(current_socket)
                new_socket = self._send_request_message(target_ip, target_port, request)
                if new_socket is None:
                    continue
                self.long_polling_sockets[new_socket] = (target_ip, target_port, request)

    @staticmethod
    def _connect(target_ip: bytes, target_port: int) -> Optional[socket.socket]:
        destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            destination_socket.connect((socket.inet_ntoa(target_ip), target_port))
            return destination_socket
        except ConnectionError:
            return None

    def _receive_message(self, message_socket: socket) -> Optional[bytes]:
        try:
            message_length = constants.to_int(message_socket.recv(constants.MESSAGE_LENGTH_BYTE_SIZE))

            if message_length == 0:
                message_socket.close()

                if message_socket in self.long_polling_sockets.keys():
                    self.long_polling_sockets.pop(message_socket)
                return None
            return message_socket.recv(message_length)

        except ConnectionError:
            return None

    def _handle_connection(self, message_socket: socket.socket) -> None:
        message = self._receive_message(message_socket)
        if message is not None:
            self._process_message(message, message_socket)

    def _listen(self) -> None:
        listening_socket = self._create_socket(constants.LISTENING_TIMEOUT)

        while self.is_listening:
            try:
                message_socket, address = listening_socket.accept()

                thread = threading.Thread(target=self._handle_connection, args=(message_socket,))
                thread.start()
            except socket.timeout:
                pass

    def _create_socket(self, timeout: float) -> socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((socket.inet_ntoa(self.ip), self.port))
        sock.listen(10)
        sock.settimeout(timeout)
        return sock

    def _process_message(self, message: bytes, message_socket: socket) -> None:
        message_type = Container[MessageType]()
        message_context = Container[bytes]()

        MessageParser.parser(message) \
            .append_type(message_type) \
            .append_bytes(message_context) \
            .parse()

        if message_type.get() == MessageType.MESSAGE:
            self.handle_message(message_context.get())
        elif message_type.get() == MessageType.REQUEST:
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
        self.long_polling_thread.join()
