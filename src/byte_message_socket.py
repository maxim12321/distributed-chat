from src.byte_message_type import ByteMessageType
from cryptography.hazmat.primitives import hashes, hmac
import socket
import sys


class ByteMessageSocket:
    def __init__(self, on_message_received):
        self.BYTE_ORDER = "big"
        self.BYTE_MESSAGE_TYPE_LENGTH = 1
        self.MESSAGE_LENGTH_LENGTH = 2
        self.PORT_ID = 8080
        self.on_message_received = on_message_received
        # To do work with on_message_received

    def send(self, ip: str, message_type: ByteMessageType, message: bytes):
        message = int(message_type).to_bytes(self.BYTE_MESSAGE_TYPE_LENGTH, self.BYTE_ORDER) + message
        message = sys.getsizeof(message).to_bytes(self.MESSAGE_LENGTH_LENGTH, self.BYTE_ORDER) + message
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_sock.connect((ip, self.PORT_ID))
        send_sock.sendall(message)

    def add_authentivation_code(self, message: bytes, key: bytes) -> bytes:
        h = hmac.HMAC(key, hashes.SHA1())
        h.update(message)
        my_hash = h.finalize()
        final_message = message + my_hash[0:20]
        return final_message

    def authenticate(self, message: bytes, key: bytes) -> bool:
        h = hmac.HMAC(key, hashes.SHA1())
        old_hmac_code = message[-20:]
        message = message[0:-20]
        h.update(message)
        new_hmac_code = h.finalize()
        return old_hmac_code == new_hmac_code
