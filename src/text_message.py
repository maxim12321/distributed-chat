from dataclasses import dataclass
from typing import Generator, Any

import constants


@dataclass
class TextMessage:
    sender_id: int
    context: bytes

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {"sender_id": self.sender_id,
                    "context": {"__bytes__": True, "bytes": constants.bytes_to_string(self.context)}}.items()
