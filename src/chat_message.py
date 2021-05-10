from dataclasses import dataclass
from typing import Any, Generator, Optional

from src.chat_message_type import ChatMessageType
from src import constants
from src.serializable import Serializable


@dataclass
class ChatMessage(Serializable):

    def __init__(self, message_type: Optional[ChatMessageType] = None,
                 sender_id: Optional[int] = None,
                 context: Optional[bytes] = None):
        self.type: Optional[ChatMessageType] = message_type
        self.sender_id: Optional[int] = sender_id
        self.context: Optional[bytes] = context

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "type": self.type,
            "sender_id": self.sender_id,
            "context": constants.bytes_to_dict(self.context)
        }.items()

    def load_from_dict(self, data_dict: dict) -> None:
        self.type = data_dict["type"]
        self.sender_id = data_dict["sender_id"]
        self.context = data_dict["context"]

    @staticmethod
    def from_dict(data: dict) -> 'ChatMessage':
        chat_message = ChatMessage()
        chat_message.load_from_dict(data)
        return chat_message