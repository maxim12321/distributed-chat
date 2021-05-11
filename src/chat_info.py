from dataclasses import dataclass
from typing import Generator, Any, Optional

from src import constants
from src.serializable import Serializable


@dataclass
class ChatInfo(Serializable):
    chat_id: Optional[int]
    chat_name: Optional[str]
    private_key: Optional[bytes]

    def __init__(self, chat_id: Optional[int] = None,
                 chat_name: Optional[str] = None,
                 private_key: Optional[bytes] = None):
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.private_key = private_key

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "chat_id": self.chat_id,
            "chat_name": self.chat_name,
            "private_key": constants.bytes_to_dict(self.private_key)
        }.items()

    def load_from_dict(self, data_dict: dict) -> None:
        self.chat_id = data_dict["chat_id"]
        self.chat_name = data_dict["chat_name"]
        self.private_key = data_dict["private_key"]
