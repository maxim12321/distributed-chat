from typing import Dict, List, Optional
from src.replication.info_key import InfoKey


class ReplicationData:
    def __init__(self):
        self.data: Dict[InfoKey, List[bytes]] = dict()

    def set_data(self, key: InfoKey, value: bytes) -> None:
        self.data[key] = [value]

    def append_data(self, key: InfoKey, value: bytes) -> None:
        if self.get_data(key) is None:
            self.data[key] = list()
        self.data[key].append(value)

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
