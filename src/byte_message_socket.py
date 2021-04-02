from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature
from src.byte_message_type import ByteMessageType
import time
import socket
import threading
from enum import IntEnum


class RequestType(IntEnum):
    REQUEST = 0
    MESSAGE = 1


class ByteMessageSocket:
    def __init__(self, ip: bytes, on_message_received: callable, on_response_received: callable):
        self.REQUEST_TYPE_BYTE_SIZE = 1
        self.MESSAGE_TYPE_BYTE_SIZE = 1
        self.MESSAGE_LENGTH_BYTE_SIZE = 2
        self.HMAC_BYTE_SIZE = 20
        self.BYTE_ORDER = "big"
        self.PORT_ID = 8080
        self.MAX_CONNECTION_TRIES_COUNT = 14
        self.WAITING_TIME_FOR_NEXT_CONNECTION = 0.313
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self.listen,
                                                 args=(ip, on_message_received, on_response_received))
        self.listening_thread.start()

    def listen(self, ip: bytes, on_message_received: callable, on_response_received: callable) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, self.PORT_ID))
        sock.listen(1)
        sock.settimeout(2.14)
        while self.is_listening:
            try:
                listen_socket, address = sock.accept()
                length = int.from_bytes(listen_socket.recv(self.MESSAGE_LENGTH_BYTE_SIZE), self.BYTE_ORDER)
                message = listen_socket.recv(length)
                request_type = int.from_bytes(message[0:self.REQUEST_TYPE_BYTE_SIZE], self.BYTE_ORDER)
                message = message[self.REQUEST_TYPE_BYTE_SIZE:]
                if request_type == RequestType.MESSAGE:
                    on_message_received(address, message)
                else:
                    answer = on_response_received(message)
                    answer = len(answer).to_bytes(self.MESSAGE_LENGTH_BYTE_SIZE, self.BYTE_ORDER) + answer
                    listen_socket.sendall(answer)
                listen_socket.close()
            except socket.timeout:
                pass

    def send_request(self, ip: bytes, message_type: ByteMessageType, message: bytes) -> bytes:
        message = self.finalize_message(RequestType.REQUEST, message_type, message)
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for x in range(self.MAX_CONNECTION_TRIES_COUNT):
            try:
                send_sock.connect((ip, self.PORT_ID))
                send_sock.sendall(message)
                send_sock.settimeout(3.14)
                try:
                    length = int.from_bytes(send_sock.recv(self.MESSAGE_LENGTH_BYTE_SIZE), self.BYTE_ORDER)
                    message = send_sock.recv(length)
                    return message
                except socket.timeout:
                    return b''
            except ConnectionRefusedError:
                time.sleep(self.WAITING_TIME_FOR_NEXT_CONNECTION)
        return b''

    def send(self, ip: bytes, message_type: ByteMessageType, message: bytes) -> bool:
        message = self.finalize_message(RequestType.MESSAGE, message_type, message)
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for x in range(self.MAX_CONNECTION_TRIES_COUNT):
            try:
                send_sock.connect((ip, self.PORT_ID))
                send_sock.sendall(message)
                return True
            except ConnectionRefusedError:
                time.sleep(self.WAITING_TIME_FOR_NEXT_CONNECTION)
        return False

    def finalize_message(self, response_type: RequestType, message_type: ByteMessageType, message: bytes) -> bytes:
        message = int(message_type).to_bytes(self.MESSAGE_TYPE_BYTE_SIZE, self.BYTE_ORDER) + message
        message = int(response_type).to_bytes(self.REQUEST_TYPE_BYTE_SIZE, self.BYTE_ORDER) + message
        message = len(message).to_bytes(self.MESSAGE_LENGTH_BYTE_SIZE, self.BYTE_ORDER) + message
        return message

    def add_authentication_code(self, message: bytes, key: bytes) -> bytes:
        h = hmac.HMAC(key, hashes.SHA1())
        h.update(message)
        my_hash = h.finalize()
        final_message = message + my_hash
        return final_message

    def authenticate(self, message: bytes, key: bytes) -> bytes:
        h = hmac.HMAC(key, hashes.SHA1())
        old_hmac_code = message[-self.HMAC_BYTE_SIZE:]
        message = message[0:-self.HMAC_BYTE_SIZE]
        h.update(message)
        try:
            h.verify(old_hmac_code)
        except InvalidSignature:
            return b''
        return message

    def __del__(self):
        self.is_listening = False
        self.listening_thread.join()
