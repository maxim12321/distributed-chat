from dataclasses import dataclass
from typing import Generator, Any, Optional
from src import constants
from src.serializable import Serializable


@dataclass
class UserInfo(Serializable):

    def __init__(self, user_id: Optional[int] = None, user_ip: Optional[bytes] = None, user_port: Optional[int] = None):
        self.user_id: Optional[int] = user_id
        self.ip: Optional[bytes] = user_ip
        self.port: Optional[int] = user_port

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "user_id": self.user_id,
            "ip": constants.bytes_to_dict(self.ip),
            "user_port": self.port
        }.items()

    def load_from_dict(self, data_dict: dict) -> None:
        self.user_id = data_dict["user_id"]
        self.ip = data_dict["ip"]
        self.port = data_dict["user_port"]

    @staticmethod
    def from_dict(data: dict) -> 'UserInfo':
        user_info = UserInfo()
        user_info.load_from_dict(data)
        return user_info
