from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import constants


class ChatMessageCipher:
    def __init__(self, user_id: int, private_key: bytes):
        self.user_id = user_id
        iv = b'0000000000000000'
        self.cipher = Cipher(algorithms.AES(private_key), modes.CBC(iv))

    def encrypt_text(self, message: str) -> bytes:
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(constants.BLOCK_SIZE).padder()
        data = self.user_id.to_bytes(constants.ID_LENGTH, constants.BYTE_ORDER) + message.encode("utf-8")
        padded_data = padder.update(data) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()

    def decrypt_text(self, token: bytes) -> (int, str):
        decryptor = self.cipher.decryptor()
        unpadder = padding.PKCS7(constants.BLOCK_SIZE).unpadder()
        message = unpadder.update(decryptor.update(token) + decryptor.finalize()) + unpadder.finalize()
        user_id = int.from_bytes(message[0:constants.ID_LENGTH], constants.BYTE_ORDER)
        message = message[constants.ID_LENGTH:].decode("utf-8")
        return user_id, message
