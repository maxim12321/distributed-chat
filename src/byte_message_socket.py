from cryptography.hazmat.primitives import hashes, hmac
from cryptography.exceptions import InvalidSignature
from src.byte_message_type import ByteMessageType
import time
import socket
import threading
import constants


class ByteMessageSocket:
    def __init__(self, ip: bytes, on_message_received: callable):
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self.listen, args=(ip, on_message_received))
        self.listening_thread.start()

    def listen(self, ip: bytes, on_message_received: callable) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, constants.PORT_ID))
        sock.listen(1)
        sock.settimeout(2.14)
        while self.is_listening:
            try:
                listen_socket, address = sock.accept()
                len = int.from_bytes(listen_socket.recv(constants.MESSAGE_LENGTH_BYTE_SIZE), constants.BYTE_ORDER)
                message = listen_socket.recv(len)
                on_message_received(address, message)
                listen_socket.close()
            except socket.timeout:
                pass

    def send(self, ip: bytes, message_type: ByteMessageType, message: bytes) -> bool:
        message = self.finalize_message(message_type, message)
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for x in range(constants.MAX_CONNECTION_TRIES_COUNT):
            try:
                send_sock.connect((ip, constants.PORT_ID))
                send_sock.sendall(message)
                return True
            except ConnectionRefusedError:
                time.sleep(constants.WAITING_TIME_FOR_NEXT_CONNECTION)
        return False

    def finalize_message(self, message_type: ByteMessageType, message: bytes) -> bytes:
        message = constants.to_bytes(message_type) + message
        message = len(message).to_bytes(constants.MESSAGE_LENGTH_BYTE_SIZE, constants.BYTE_ORDER) + message
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
            return None
        return message

    def __del__(self):
        self.is_listening = False
        self.listening_thread.join()
