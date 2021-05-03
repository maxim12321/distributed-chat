from dataclasses import dataclass
from typing import Generator, Any, Optional
from src import constants
from serializable import Serializable

import constants


@dataclass
class TextMessage(Serializable):

    def __init__(self, sender_id: Optional[int] = None, context: Optional[bytes] = None):
        self.sender_id: Optional[int] = sender_id
        self.context: Optional[bytes] = context

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "sender_id": self.sender_id,
            "context": constants.bytes_to_dict(self.context)
        }.items()

    def load_from_dict(self, data_dict: dict) -> None:
        self.sender_id = data_dict["sender_id"]
        self.context = data_dict["context"]