from cryptography.hazmat.primitives import hashes, hmac
from src.byte_message_type import ByteMessageType
import socket
import sys
import threading


class ByteMessageSocket:
    def __init__(self, ip: str, on_message_received: callable):
        self.MESSAGE_TYPE_BYTE_SIZE = 1
        self.MESSAGE_LENGTH_BYTE_SIZE = 2
        self.HMAC_BYTE_SIZE = 20
        self.BYTE_ORDER = "big"
        self.PORT_ID = 8080
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self.listen, args=(ip, on_message_received))
        self.listening_thread.start()

    def listen(self, ip: str, on_message_received: callable) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, int(self.PORT_ID)))
        sock.listen(1)
        sock.settimeout(2.14)
        while self.is_listening:
            try:
                listen_socket, address = sock.accept()
                len = int.from_bytes(listen_socket.recv(self.MESSAGE_LENGTH_BYTE_SIZE), self.BYTE_ORDER)
                message = listen_socket.recv(len)
                on_message_received(address, message)
                listen_socket.close()
            except:
                None

    def send(self, ip: str, message_type: ByteMessageType, message: bytes) -> bool:
        message = int(message_type).to_bytes(self.MESSAGE_TYPE_BYTE_SIZE, self.BYTE_ORDER) + message
        message = sys.getsizeof(message).to_bytes(self.MESSAGE_LENGTH_BYTE_SIZE, self.BYTE_ORDER) + message
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_sock.connect((ip, self.PORT_ID))
            send_sock.sendall(message)
        except:
            return False
        return True

    def add_authentivation_code(self, message: bytes, key: bytes) -> bytes:
        h = hmac.HMAC(key, hashes.SHA1())
        h.update(message)
        my_hash = h.finalize()
        final_message = message + my_hash[0:self.HMAC_BYTE_SIZE]
        return final_message

    def authenticate(self, message: bytes, key: bytes) -> bool:
        h = hmac.HMAC(key, hashes.SHA1())
        old_hmac_code = message[-self.HMAC_BYTE_SIZE:]
        message = message[0:-self.HMAC_BYTE_SIZE]
        h.update(message)
        new_hmac_code = h.finalize()
        return old_hmac_code == new_hmac_code

    def __del__(self):
        self.is_listening = False
        self.listening_thread.join()
