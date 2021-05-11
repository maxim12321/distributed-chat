from typing import Dict, List, Optional, Generator, Any

from src import constants
from src.replication.info_key import InfoKey
from src.serializable import Serializable


class ReplicationData(Serializable):
    def __init__(self) -> None:
        self.data: Dict[InfoKey, List[bytes]] = dict()

    def __iter__(self) -> Generator[str, Any, None]:
        for info_key, value in self.data.items():
            yield str(info_key), list(map(constants.bytes_to_dict, value))

    def load_from_dict(self, data: dict) -> None:
        self.data = {}
        for key, value in data.items():
            self.data[InfoKey.from_string(key)] = value

    def set_data(self, key: InfoKey, value: bytes) -> None:
        self.data[key] = [value]

    def append_data(self, key: InfoKey, value: bytes) -> int:
        if self.get_data(key) is None:
            self.data[key] = list()
        self.data[key].append(value)
        return len(self.data[key]) - 1

    def try_edit_data(self, key: InfoKey, index: int, new_value: bytes) -> bool:
        if key not in self.data:
            return False
        if index < 0 or index >= len(self.data[key]):
            return False
        if self.data[key][index] == new_value:
            return False

        self.data[key][index] = new_value
        return True

    def remove_data(self, keys: List[InfoKey]) -> None:
        for key in keys:
            if key in self.data.keys():
                self.data.pop(key)

    def update_data(self, new_data: 'ReplicationData') -> None:
        for key, values in new_data.data.items():
            self.data[key] = list()
            for value in values:
                self.append_data(key, value)

    def get_data(self, key: InfoKey) -> Optional[List[bytes]]:
        if key in self.data.keys():
            return self.data[key]
        return None

    def get_replication_data(self, keys: List[InfoKey]) -> 'ReplicationData':
        replication_data = ReplicationData()

        for key in keys:
            if self.get_data(key) is None:
                continue

            for data in self.get_data(key):
                replication_data.append_data(key, data)
        return replication_data

    def __str__(self) -> str:
        return f"ReplicationData:{self.data}"
