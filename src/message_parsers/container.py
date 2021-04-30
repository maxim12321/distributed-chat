from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


@dataclass
class Container(Generic[T]):
    def __init__(self, value: Optional[T] = None):
        self.value: Optional[T] = value

    def get(self) -> Optional[T]:
        return self.value

    def set(self, value: T) -> None:
        self.value = value
