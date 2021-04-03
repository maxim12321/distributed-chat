from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature
from byte_message_type import ByteMessageType
import time
import socket
import threading
import constants
from enum import IntEnum


class RequestType(IntEnum):
    REQUEST = 0
    MESSAGE = 1


class ByteMessageSocket:
    def __init__(self, ip: bytes, on_message_received: callable, on_request_received: callable):
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self.listen,
                                                 args=(ip, on_message_received, on_request_received))
        self.listening_thread.start()

    def listen(self, ip: bytes, on_message_received: callable, on_request_received: callable) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, constants.PORT_ID))
        sock.listen(1)
        sock.settimeout(2.14)
        while self.is_listening:
            try:
                listen_socket, address = sock.accept()
                length = constants.to_int(listen_socket.recv(constants.MESSAGE_LENGTH_BYTE_SIZE))
                if (length == 0):
                    listen_socket.close()
                    continue
                listen_socket.settimeout(2.14)
                try:
                    message = listen_socket.recv(length)
                    request_type = constants.to_int(message[0:constants.REQUEST_TYPE_BYTE_SIZE])
                    message = message[constants.REQUEST_TYPE_BYTE_SIZE:]
                    if request_type == RequestType.MESSAGE:
                        on_message_received(address, message)
                    else:
                        answer = on_request_received(message)
                        if len(answer) != 0:
                            answer = constants.to_bytes_message_length(len(answer)) + answer
                            listen_socket.sendall(answer)
                except socket.timeout:
                    pass
                listen_socket.close()
            except socket.timeout:
                pass

    def create_send_socket(self, ip: bytes) -> socket:
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for x in range(constants.MAX_CONNECTION_TRIES_COUNT):
            try:
                send_sock.connect((ip, constants.PORT_ID))
                return send_sock
            except ConnectionRefusedError:
                time.sleep(constants.WAITING_TIME_FOR_NEXT_CONNECTION)
        return None

    def send_request(self, ip: bytes, message_type: ByteMessageType, message: bytes) -> bytes:
        message = self.finalize_message(RequestType.REQUEST, message_type, message)
        send_sock = self.create_send_socket(ip)
        if send_sock == None:
            return b''
        send_sock.sendall(message)
        send_sock.settimeout(3.14)
        try:
            length = constants.to_int(send_sock.recv(constants.MESSAGE_LENGTH_BYTE_SIZE))
            message = send_sock.recv(length)
            return message
        except socket.timeout:
            return b''

    def send(self, ip: bytes, message_type: ByteMessageType, message: bytes) -> bool:
        message = self.finalize_message(RequestType.MESSAGE, message_type, message)
        send_sock = self.create_send_socket(ip)
        if send_sock == None:
            return False
        send_sock.sendall(message)
        return True

    def finalize_message(self, request_type: RequestType, message_type: ByteMessageType, message: bytes) -> bytes:
        message = constants.to_bytes_message_type(message_type) + message
        message = constants.to_bytes_request_type(request_type) + message
        message = constants.to_bytes_message_length(len(message)) + message
        return message

    def add_authentication_code(self, message: bytes, key: bytes) -> bytes:
        h = hmac.HMAC(key, hashes.SHA1())
        h.update(message)
        my_hash = h.finalize()
        final_message = message + my_hash
        return final_message

    def authenticate(self, message: bytes, key: bytes) -> bytes:
        h = hmac.HMAC(key, hashes.SHA1())
        old_hmac_code = message[-constants.HMAC_BYTE_SIZE:]
        message = message[0:-constants.HMAC_BYTE_SIZE]
        h.update(message)
        try:
            h.verify(old_hmac_code)
        except InvalidSignature:
            return b''
        return message

    def __del__(self):
        self.is_listening = False
        self.listening_thread.join()
