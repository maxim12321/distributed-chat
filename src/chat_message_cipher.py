from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ChatMessageCipher:
    def __init__(self, user_id: int, private_key: bytes):
        self.USER_ID_LENGTH = 2
        self.BYTE_ORDER = "big"
        self.BLOCK_SIZE = 32
        self.user_id = user_id
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA1(),
            length=16,
            salt=private_key,
            iterations=2,
        )
        iv = kdf.derive(private_key)
        self.cipher = Cipher(algorithms.AES(private_key), modes.CBC(iv))

    def encrypt_text(self, message: str) -> bytes:
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(self.BLOCK_SIZE).padder()
        data = self.user_id.to_bytes(self.USER_ID_LENGTH, self.BYTE_ORDER) + message.encode("utf-8")
        padded_data = padder.update(data) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()

    def decrypt_text(self, token: bytes) -> (int, str):
        decryptor = self.cipher.decryptor()
        unpadder = padding.PKCS7(self.BLOCK_SIZE).unpadder()
        message = unpadder.update(decryptor.update(token) + decryptor.finalize()) + unpadder.finalize()
        user_id = int.from_bytes(message[0:self.USER_ID_LENGTH], self.BYTE_ORDER)
        message = message[self.USER_ID_LENGTH:].decode("utf-8")
        return user_id, message
