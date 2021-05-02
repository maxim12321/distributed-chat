from abc import ABC, abstractmethod
from typing import Any, Generator


class Serializable(ABC):
    @abstractmethod
    def __iter__(self) -> Generator[str, Any, None]:
        pass
    
    @abstractmethod
    def load_from_dict(self, data: dict) -> None:
        pass
