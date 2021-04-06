from typing import Dict, Optional, List
from src.replication.info_key import InfoKey


class ReplicationInfo:
    def __init__(self):
        self.info: Dict[InfoKey, int] = dict()

    def add_info(self, key: InfoKey, value: int) -> None:
        self.info[key] = value

    def get_value(self, key: InfoKey) -> Optional[int]:
        if key in self.info.keys():
            return self.info[key]
        return None

    def get_keys(self) -> List[InfoKey]:
        return list(self.info.keys())

    def remove_keys(self, keys: List[InfoKey]) -> None:
        for key in keys:
            self.info.pop(key)

    def update_info(self, other_info: 'ReplicationInfo') -> None:
        self.info.update(other_info.info)

    def get_info_to_update(self, new_info: 'ReplicationInfo') -> 'ReplicationInfo':
        info_to_update = ReplicationInfo()

        for key, value in new_info.info.items():
            if self.get_value(key) != value:
                info_to_update.add_info(key, value)
        return info_to_update

    def decrement_values(self) -> None:
        for key in self.info.keys():
            self.info[key] -= 1

    def get_keys_to_remove(self) -> List[InfoKey]:
        keys_to_remove = [key for key, value in self.info.items() if value == 0]
        return list(keys_to_remove)

    def get_keys_with_smaller_id(self, data_id: int) -> List[InfoKey]:
        keys: List[InfoKey] = list()

        for key in self.info.keys():
            if key.data_id <= data_id:
                keys.append(key)
        return keys

    def __str__(self) -> str:
        return f"ReplicationInfo:{self.info}"
