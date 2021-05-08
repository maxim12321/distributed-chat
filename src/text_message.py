from dataclasses import dataclass
from typing import Generator, Any

from src.chat_message_type import ChatMessageType
import constants


@dataclass
class ChatMessage:
    type: ChatMessageType
    sender_id: int
    context: bytes

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "type": self.type,
            "sender_id": self.sender_id,
            "context": constants.bytes_to_dict(self.context)
        }.items()
