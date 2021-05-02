from typing import Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.hmac import HMAC

from src import constants


class Authentication:
    @staticmethod
    def add_authentication_code(message: bytes, key: bytes) -> bytes:
        hmac = HMAC(key, SHA1())
        hmac.update(message)
        authentication_code = hmac.finalize()

        return message + authentication_code

    @staticmethod
    def authenticate(message: bytes, key: bytes) -> Optional[bytes]:
        hmac = HMAC(key, SHA1())
        message_code = message[-constants.HMAC_BYTE_SIZE:]
        message = message[0:-constants.HMAC_BYTE_SIZE]

        hmac.update(message)
        try:
            hmac.verify(message_code)
        except InvalidSignature:
            return None

        return message
