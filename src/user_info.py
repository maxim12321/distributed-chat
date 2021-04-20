from dataclasses import dataclass
from typing import Generator, Any


@dataclass
class UserInfo:
    user_id: int

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "user_id": self.user_id
        }.items()
