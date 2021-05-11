from dataclasses import dataclass
from typing import Generator, Any, Optional

from src import constants
from src.serializable import Serializable


@dataclass
class ChatInfo(Serializable):
    chat_id: Optional[int]
    private_key: Optional[bytes]

    def __init__(self, chat_id: Optional[int] = None, private_key: Optional[bytes] = None):
        self.chat_id = chat_id
        self.private_key = private_key

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "chat_id": self.chat_id,
            "private_key": constants.bytes_to_dict(self.private_key)
        }.items()

    def load_from_dict(self, data_dict: dict) -> None:
        self.chat_id = data_dict["chat_id"]
        self.private_key = data_dict["private_key"]
