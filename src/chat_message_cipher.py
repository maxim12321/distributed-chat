from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from src import constants


class ChatMessageCipher:

    def __init__(self, private_key: bytes):
        iv = b'0' * constants.BLOCK_SIZE_BYTES
        self.cipher = Cipher(algorithms.AES(private_key), modes.CBC(iv))

    def encrypt_data(self, data: bytes) -> bytes:
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(constants.BLOCK_SIZE_BYTES * 8).padder()
        padded_data = padder.update(data) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        decryptor = self.cipher.decryptor()
        unpadder = padding.PKCS7(constants.BLOCK_SIZE_BYTES * 8).unpadder()
        data = unpadder.update(decryptor.update(encrypted_data) + decryptor.finalize()) + unpadder.finalize()
        return data
