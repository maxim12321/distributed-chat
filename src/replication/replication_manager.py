from typing import List, Optional, Tuple
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


class ReplicationManager:
    def __init__(self):
        self.REPLICATION_COEFFICIENT = 5

        self.info = ReplicationInfo()
        self.data = ReplicationData()

    def get_single_data(self, key: InfoKey) -> Optional[bytes]:
        data = self.data.get_data(key)
        return None if data is None else data[0]

    def get_data(self, key: InfoKey) -> Optional[List[bytes]]:
        return self.data.get_data(key)

    def get_info(self) -> ReplicationInfo:
        return self.info

    def set_data(self, key: InfoKey, data: bytes) -> None:
        self.info.add_info(key, self.REPLICATION_COEFFICIENT)
        self.data.set_data(key, data)

    def append_data(self, key: InfoKey, data: bytes) -> None:
        self.info.add_info(key, self.REPLICATION_COEFFICIENT)
        self.data.append_data(key, data)

    def drop_data_with_id_inside(self, left_id: int, right_id: int) -> None:
        keys_to_remove = self.info.get_keys_with_id_inside(left_id, right_id)
        self.info.remove_keys(keys_to_remove)
        self.data.remove_data(keys_to_remove)

    # Update all values, for that self became successor
    def move_all_from_predecessor(self) -> Tuple[ReplicationInfo, ReplicationData]:
        incremented_keys = self.info.increment_all_equal_to(self.REPLICATION_COEFFICIENT - 1)
        return self.info.get_info_by_keys(incremented_keys), self.data.get_replication_data(incremented_keys)

    def get_info_to_update(self, new_info: ReplicationInfo) -> ReplicationInfo:
        return self.info.get_info_to_update(new_info)

    def get_key_replication(self, key: InfoKey) -> Tuple[ReplicationInfo, ReplicationData]:
        return self.info.get_info_by_keys([key]), self.data.get_replication_data([key])

    def get_data_by_keys(self, keys: List[InfoKey]) -> ReplicationData:
        return self.data.get_replication_data(keys)

    # Updates self.info from new_info, removes unnecessary data, returns ReplicationInfo, containing all updated values
    def update_info(self, new_info: ReplicationInfo) -> ReplicationInfo:
        new_info.decrement_values()
        updated_info = self.info.get_info_to_update(new_info)
        self.info.update_info(updated_info)

        keys_to_remove = self._remove_keys_from_info(updated_info)
        self.info.remove_keys(keys_to_remove)
        self.data.remove_data(keys_to_remove)

        return updated_info

    def update(self, new_info: ReplicationInfo, new_data: ReplicationData) -> Tuple[ReplicationInfo, ReplicationData]:
        new_info.decrement_values()
        return self.set(new_info, new_data)

    # Updates info and data, removes unnecessary, returns info, containing all updated values, and corresponding data
    def set(self, new_info: ReplicationInfo, new_data: ReplicationData) -> Tuple[ReplicationInfo, ReplicationData]:
        updated_info = self.info.get_info_to_update(new_info)
        keys_to_remove = self._remove_keys_from_info(new_info)

        self.info.update_info(updated_info)
        self.data.update_data(new_data)

        self.data.remove_data(keys_to_remove)
        return updated_info, self.data.get_replication_data(updated_info.get_keys())

    @staticmethod
    def _remove_keys_from_info(new_info: ReplicationInfo) -> List[InfoKey]:
        keys_to_remove = new_info.get_keys_to_remove()
        new_info.remove_keys(keys_to_remove)
        return keys_to_remove

    def __str__(self) -> str:
        return f"Info={self.info},\nData={self.data}.\n"
