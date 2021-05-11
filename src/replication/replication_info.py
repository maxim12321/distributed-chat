from copy import deepcopy
from typing import Dict, List, Optional, Generator, Any

from src.replication.info_key import InfoKey
from src.replication.info_value import InfoValue
from src.serializable import Serializable


class ReplicationInfo(Serializable):
    def __init__(self) -> None:
        self.info: Dict[InfoKey, InfoValue] = dict()

    def __iter__(self) -> Generator[str, Any, None]:
        for info_key, value in self.info.items():
            yield str(info_key), dict(value)

    def load_from_dict(self, data: dict) -> None:
        self.info = {}
        for key_string, value_dict in data.items():
            self.info[InfoKey.from_string(key_string)] = InfoValue.from_dict(value_dict)

    def add_info(self, key: InfoKey, value: InfoValue) -> None:
        self.info[key] = value

    def get_value(self, key: InfoKey) -> Optional[InfoValue]:
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
            if self.get_value(key) is None and value.current_index <= 0:
                continue

            if self.get_value(key) is None or self.get_value(key).current_index != value.current_index:
                info_to_update.add_info(key, value)
        return info_to_update

    def increment_all_equal_to(self, old_value: int) -> List[InfoKey]:
        incremented_keys: List[InfoKey] = list()

        for key in self.info.keys():
            if self.get_value(key).current_index == old_value:
                self.info[key].current_index += 1
                incremented_keys.append(key)
        return incremented_keys

    def update_first_nodes(self, starting_value: int, current_id: int) -> None:
        for key in self.info.keys():
            if self.info[key].current_index == starting_value:
                self.info[key].first_node_id = current_id

    def decrement_values(self) -> None:
        for key in self.info.keys():
            self.info[key].current_index -= 1

    def get_decremented_info(self) -> 'ReplicationInfo':
        new_info = deepcopy(self)
        new_info.decrement_values()
        return new_info

    # Returns list of keys, that shouldn't be stored in current node
    def get_keys_to_remove(self) -> List[InfoKey]:
        keys_to_remove = [key for key, value in self.info.items() if value.current_index <= 0]
        return list(keys_to_remove)

    def get_keys_with_id(self, node_id: int) -> List[InfoKey]:
        keys_with_id = [key for key, value in self.info.items() if value.first_node_id == node_id]
        return list(keys_with_id)

    # Returns list of keys, that data id's are inside segment (left_id; right_id]
    def get_keys_with_id_inside(self, left_id: int, right_id: int) -> List[InfoKey]:
        keys: List[InfoKey] = list()

        for key in self.info.keys():
            if self.is_inside(left_id, right_id, key.data_id):
                keys.append(key)
        return keys

    @staticmethod
    def is_inside(left: int, right: int, value: int) -> bool:
        if left < right:
            return left <= value <= right
        return value >= left or value <= right

    def __str__(self) -> str:
        return f"ReplicationInfo:{self.info}"
