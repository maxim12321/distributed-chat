import select
import threading
from dataclasses import dataclass
import socket
from typing import Dict, Callable, List, Tuple

from src.chat_message_type import ChatMessageType
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.message_parser import MessageParser
from src.message_parsers.container import Container
from src.senders.socket_message_sender import SocketMessageSender
import src.constants as constants


@dataclass
class LongPollInfo:
    long_poll_id: int
    message_socket: socket.socket


@dataclass
class RequestInfo:
    long_polling_id: int
    request: bytes


class LongPollingRequests:
    def __init__(self, message_sender: SocketMessageSender,
                 on_long_polling_canceled: Callable[[bytes], None]) -> None:
        self.long_polling_request: Dict[bytes, List[LongPollInfo]] = {}
        self.long_polling_sockets: Dict[socket.socket, RequestInfo] = {}

        self.message_sender = message_sender
        self.message_sender.set_long_polling_callback(self.on_long_polling_received)

        self.is_listening = True
        self.check_thread = threading.Thread(target=self._check_sockets)
        self.check_thread.start()

        self.on_long_polling_canceled = on_long_polling_canceled

    def send_answer(self, request: bytes, answer: bytes) -> None:
        if request not in self.long_polling_request:
            return

        message = MessageBuilder.builder()\
            .append_bytes(answer)\
            .build()

        for info in self.long_polling_request[request]:
            try:
                info.message_socket.sendall(message)
            except ConnectionError:
                self.long_polling_request[request].remove(info)

    def on_long_polling_received(self, message_socket: socket.socket, request: bytes) -> None:
        long_polling_id = Container[int]()
        request_message = Container[bytes]()
        MessageParser.parser(request) \
            .append_id(long_polling_id) \
            .append_bytes(request_message) \
            .parse()

        if request_message.get() not in self.long_polling_request.keys():
            self.long_polling_request[request_message.get()] = []
        self.long_polling_request[request_message.get()].append(LongPollInfo(long_polling_id.get(), message_socket))

        message_socket.send(b'OK')

    def add_long_polling_request(self, target_ip: bytes, target_port: int,
                                 request: bytes, long_polling_id: int) -> None:
        current_socket = self.message_sender.send_long_polling_message(target_ip, target_port, request, long_polling_id)
        if current_socket is None:
            self.on_long_polling_canceled(request)
            return
        current_socket.recv(2)

        self.long_polling_sockets[current_socket] = RequestInfo(long_polling_id, request)

    def cancel_long_polling_request(self, long_polling_id: int) -> None:
        for key in self.long_polling_request.keys():
            polls_to_remove: List[LongPollInfo] = []

            for info in self.long_polling_request[key]:
                if info.long_poll_id == long_polling_id:
                    info.message_socket.shutdown(socket.SHUT_RDWR)
                    polls_to_remove.append(info)

            for info in polls_to_remove:
                self.long_polling_request[key].remove(info)

    def _check_sockets(self) -> None:
        while self.is_listening:
            sockets = self.long_polling_sockets.keys()
            if len(sockets) == 0:
                continue

            read_sockets, _, _ = select.select(sockets, [], [], constants.SELECT_TIMOUT)
            for read_socket in read_sockets:
                answer = self.message_sender.receive_message(read_socket)

                if answer is None:
                    self.on_long_polling_canceled(self.long_polling_sockets[read_socket].request)
                    self.long_polling_sockets.pop(read_socket)
                else:
                    self.message_sender.handle_message(answer)

    @staticmethod
    def build_long_polling_request(value_id: int, chat_message_type: ChatMessageType) -> bytes:
        return MessageBuilder.builder() \
            .append_id(value_id) \
            .append_type(chat_message_type) \
            .build()

    @staticmethod
    def parse_long_polling_request(request: bytes) -> Tuple[int, ChatMessageType]:
        value_id: Container[int] = Container()
        chat_message_type: Container[ChatMessageType] = Container()

        MessageParser.parser(request) \
            .append_id(value_id) \
            .append_type(chat_message_type) \
            .parse()
        return value_id.get(), ChatMessageType(chat_message_type.get())

    def __del__(self) -> None:
        self.is_listening = False
        self.check_thread.join()
