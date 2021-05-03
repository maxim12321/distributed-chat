from dataclasses import dataclass
from typing import Generator, Any, Optional
from src import constants
from serializable import Serializable


@dataclass
class UserInfo(Serializable):

    def __init__(self, user_id: Optional[int] = None, user_ip: Optional[bytes] = None):
        self.user_id: Optional[int] = user_id
        self.ip: Optional[bytes] = user_ip

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "user_id": self.user_id,
            "ip": constants.bytes_to_dict(self.ip)
        }.items()

    def load_from_dict(self, data_dict: dict) -> None:
        self.user_id = data_dict["user_id"]
        self.ip = data_dict["ip"]
