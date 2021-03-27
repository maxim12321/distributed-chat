import os
import base64


class Chat:
    def __init__(self, name: str):
        self.PRIVATE_KEY_LENGTH = 16
        self.private_key = None
        self.chat_id = None
        self.name = name

    def generate_private_key(self) -> None:
        self.private_key = os.urandom(self.PRIVATE_KEY_LENGTH)

    def generate_invite_link(self, ip_address: bytes) -> str:
        link_bytes = base64.b64encode(self.private_key + ip_address)
        return link_bytes.decode("utf-8")

    def parse_invite_link(self, link: str) -> None:
        link_bytes = base64.b64decode(link)
        self.private_key = link_bytes[:self.PRIVATE_KEY_LENGTH]
