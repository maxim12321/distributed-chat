import os
import base64


class Chat:
    PRIVATE_KYE_LENGTH: int
    private_key: bytes
    chat_id: int
    name: str

    def __init__(self, name: str):
        self.PRIVATE_KYE_LENGTH = 8
        self.name = name

    def generate_private_key(self):
        self.private_key = os.urandom(self.PRIVATE_KYE_LENGTH)
       
    def generate_invite_link(self, ip_address: bytes) -> str:
        link_bytes = base64.b64encode(self.private_key + ip_address)
        return link_bytes.decode("utf-8")

    def parse_invite_link(self, link: str):
        link_bytes = base64.b64decode(link)
        self.private_key = link_bytes[:self.PRIVATE_KYE_LENGTH]
