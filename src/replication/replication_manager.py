from typing import List, Optional
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


class ReplicationManager:
    def __init__(self):
        self.REPLICATION_COEFFICIENT = 5

        self.info = ReplicationInfo()
        self.data = ReplicationData()

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

    def drop_data_with_smaller_id(self, data_id: int):
        keys_to_remove = self.info.get_keys_with_smaller_id(data_id)
        self.info.remove_keys(keys_to_remove)
        self.data.remove_data(keys_to_remove)

    def get_info_to_update(self, new_info: ReplicationInfo) -> ReplicationInfo:
        return self.info.get_info_to_update(new_info)

    def get_data_by_keys(self, keys: List[InfoKey]) -> ReplicationData:
        return self.data.get_replication_data(keys)

    def update_info(self, new_info: ReplicationInfo) -> ReplicationInfo:
        new_info.decrement_values()
        keys_to_remove = self._remove_keys_from_info(new_info)
        self.info.remove_keys(keys_to_remove)
        self.data.remove_data(keys_to_remove)

        return self._get_updated_info(new_info)

    def update(self, new_info: ReplicationInfo, new_data: ReplicationData) -> ReplicationInfo:
        new_info.decrement_values()
        return self.set(new_info, new_data)

    def set(self, new_info: ReplicationInfo, new_data: ReplicationData) -> ReplicationInfo:
        new_data.remove_data(self._remove_keys_from_info(new_info))

        self.data.update_data(new_data)
        return self._get_updated_info(new_info)

    def _get_updated_info(self, new_info: ReplicationInfo) -> ReplicationInfo:
        updated_info = self.info.get_info_to_update(new_info)
        self.info.update_info(new_info)
        return updated_info

    @staticmethod
    def _remove_keys_from_info(new_info: ReplicationInfo) -> List[InfoKey]:
        keys_to_remove = new_info.get_keys_to_remove()
        new_info.remove_keys(keys_to_remove)
        return keys_to_remove

    def __str__(self) -> str:
        return f"Info={self.info},\nData={self.data}.\n"
