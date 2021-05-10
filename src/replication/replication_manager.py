from typing import List, Optional, Tuple

from src import constants
from src.replication.info_key import InfoKey
from src.replication.info_value import InfoValue
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


class ReplicationManager:
    def __init__(self):
        self.info = ReplicationInfo()
        self.data = ReplicationData()

    def get_single_data(self, key: InfoKey) -> Optional[bytes]:
        data = self.data.get_data(key)
        return None if data is None else data[0]

    def get_data(self, key: InfoKey) -> Optional[List[bytes]]:
        return self.data.get_data(key)

    def get_info(self) -> ReplicationInfo:
        return self.info

    def get_replication_coefficient(self, key: InfoKey) -> Optional[int]:
        if self.info.get_value(key) is None:
            return None
        return self.info.get_value(key).current_index

    def set_data(self, current_id: int, key: InfoKey, data: bytes) -> None:
        self.info.add_info(key, InfoValue(constants.REPLICATION_FACTOR, current_id))
        self.data.set_data(key, data)

    def append_data(self, current_id: int, key: InfoKey, data: bytes,
                    current_index: Optional[int] = None) -> int:
        if current_index is None:
            current_index = constants.REPLICATION_FACTOR
        self.info.add_info(key, InfoValue(current_index, current_id))
        return self.data.append_data(key, data)

    def try_edit_data(self, key: InfoKey, index: int, new_data: bytes) -> bool:
        return self.data.try_edit_data(key, index, new_data)

    def drop_data_with_id_inside(self, left_id: int, right_id: int) -> None:
        keys_to_remove = self.info.get_keys_with_id_inside(left_id, right_id)
        self.info.remove_keys(keys_to_remove)
        self.data.remove_data(keys_to_remove)

    def update_first_nodes(self, current_id: int) -> None:
        self.info.update_first_nodes(constants.REPLICATION_FACTOR, current_id)

    # Update all values, for that self became successor
    def move_all_from_predecessor(self, current_id: int) -> Tuple[ReplicationInfo, ReplicationData]:
        incremented_keys = self.info.increment_all_equal_to(constants.REPLICATION_FACTOR - 1)
        self.update_first_nodes(current_id)

        return self.info.get_info_by_keys(incremented_keys), self.data.get_replication_data(incremented_keys)

    # Add info, excluding overlapping keys, and remove unnecessary replications
    def update_replication_info(self, current_id: int, new_info: ReplicationInfo) -> ReplicationInfo:
        overlapping_keys = new_info.get_keys_with_id(current_id)
        new_info.remove_keys(overlapping_keys)

        info_to_update = self.info.get_info_to_update(new_info)
        self.info.update_info(new_info)

        keys_to_remove = self.info.get_keys_to_remove()
        self.info.remove_keys(keys_to_remove)
        self.data.remove_data(keys_to_remove)

        return info_to_update

    def update_replication_data(self, new_data: ReplicationData) -> None:
        self.data.update_data(new_data)

    def update_replication(self, current_id: int,
                           new_info: ReplicationInfo,
                           new_data: ReplicationData) -> Tuple[ReplicationInfo, ReplicationData]:
        self.update_replication_data(new_data)

        updated_info = self.update_replication_info(current_id, new_info)
        return updated_info, self.data.get_replication_data(updated_info.get_keys())

    def set_replication(self, new_info: ReplicationInfo, new_data: ReplicationData) -> None:
        self.info.update_info(new_info)
        self.data.update_data(new_data)

    def get_key_replication(self, key: InfoKey) -> Tuple[ReplicationInfo, ReplicationData]:
        return self.info.get_info_by_keys([key]), self.data.get_replication_data([key])

    def get_data_by_keys(self, keys: List[InfoKey]) -> ReplicationData:
        return self.data.get_replication_data(keys)

    def __str__(self) -> str:
        return f"Info={self.info},\nData={self.data}.\n"
