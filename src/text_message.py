from dataclasses import dataclass
from typing import Any, Generator, Optional

from src import constants
from src.serializable import Serializable


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

    @staticmethod
    def from_dict(data: dict) -> 'TextMessage':
        text_message = TextMessage()
        text_message.load_from_dict(data)
        return text_message
