from dataclasses import dataclass
from typing import Generator, Any

from src.serializable import Serializable


@dataclass
class InfoValue(Serializable):
    current_index: int
    first_node_id: int

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "index": self.current_index,
            "first_id": self.first_node_id
        }.items()

    def load_from_dict(self, data: dict) -> None:
        self.current_index = data["index"]
        self.first_node_id = data["first_id"]

    @staticmethod
    def from_dict(data: dict) -> 'InfoValue':
        value = InfoValue(0, 0)
        value.load_from_dict(data)
        return value
