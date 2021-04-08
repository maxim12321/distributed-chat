from typing import Dict, List, Optional
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

    def get_size(self) -> int:
        return len(self.info.keys())

    def remove_keys(self, keys: List[InfoKey]) -> None:
        for key in keys:
            if key in self.info.keys():
                self.info.pop(key)

    def update_info(self, other_info: 'ReplicationInfo') -> None:
        self.info.update(other_info.info)

    def get_info_by_keys(self, keys: List[InfoKey]) -> 'ReplicationInfo':
        replication_info = ReplicationInfo()

        for key in keys:
            if self.get_value(key) is None:
                continue

            replication_info.add_info(key, self.get_value(key))
        return replication_info

    # Returns ReplicationInfo containing all keys from new_info, that differ from self.info
    def get_info_to_update(self, new_info: 'ReplicationInfo') -> 'ReplicationInfo':
        info_to_update = ReplicationInfo()

        for key, value in new_info.info.items():
            # If key is not present and it shouldn't be stored, skip it (no further updates needed)
            if self.get_value(key) is None and value <= 0:
                continue

            if self.get_value(key) != value:
                info_to_update.add_info(key, value)
        return info_to_update

    def increment_all_equal_to(self, old_value: int) -> List[InfoKey]:
        incremented_keys: List[InfoKey] = list()

        for key in self.info.keys():
            if self.get_value(key) == old_value:
                self.info[key] += 1
                incremented_keys.append(key)
        return incremented_keys

    def decrement_values(self) -> None:
        for key in self.info.keys():
            self.info[key] -= 1

    # Returns list of keys, that shouldn't be stored in current node
    def get_keys_to_remove(self) -> List[InfoKey]:
        keys_to_remove = [key for key, value in self.info.items() if value <= 0]
        return list(keys_to_remove)

    # Returns list of keys, that data id's are inside segment (left_id; right_id]
    def get_keys_with_id_inside(self, left_id: int, right_id: int) -> List[InfoKey]:
        keys: List[InfoKey] = list()

        for key in self.info.keys():
            if self.is_inside_right(left_id, right_id, key.data_id):
                keys.append(key)
        return keys

    @staticmethod
    def is_inside_right(left: int, right: int, value: int) -> bool:
        if left < right:
            return left < value <= right
        return value > left or value <= right

    def __str__(self) -> str:
        return f"ReplicationInfo:{self.info}"
