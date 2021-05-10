from abc import ABC, abstractmethod
from typing import List, Optional

from src.dht.node_info import NodeInfo
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


class NodeRequestSender(ABC):
    @abstractmethod
    def ping(self, node: NodeInfo) -> bool:
        pass

    @abstractmethod
    def request_successor(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        pass

    @abstractmethod
    def request_next_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        pass

    @abstractmethod
    def request_previous_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        pass

    @abstractmethod
    def request_preceding_finger(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        pass

    @abstractmethod
    def request_successor_list(self, node: NodeInfo) -> Optional[List[NodeInfo]]:
        pass

    @abstractmethod
    def propose_finger_update(self, node: NodeInfo, node_to_update: NodeInfo, finger_number: int) -> Optional[bytes]:
        pass

    @abstractmethod
    def propose_predecessor(self, node: NodeInfo, node_to_propose: NodeInfo) -> Optional[bytes]:
        pass

    @abstractmethod
    def request_replication_info(self, node: NodeInfo) -> Optional[ReplicationInfo]:
        pass

    @abstractmethod
    def request_data_by_keys(self, node: NodeInfo, keys: List[InfoKey]) -> Optional[ReplicationData]:
        pass

    @abstractmethod
    def update_replication_info(self, node: NodeInfo, new_info: ReplicationInfo) -> Optional[bytes]:
        pass

    @abstractmethod
    def update_replication(self, node: NodeInfo,
                           new_info: ReplicationInfo, new_data: ReplicationData) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_value(self, node: NodeInfo, key: InfoKey) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_all_values(self, node: NodeInfo, key: InfoKey) -> Optional[List[bytes]]:
        pass

    @abstractmethod
    def set_value(self, node: NodeInfo, key: InfoKey, value: bytes) -> Optional[bytes]:
        pass

    @abstractmethod
    def append_value(self, node: NodeInfo, key: InfoKey, value: bytes) -> Optional[int]:
        pass

    @abstractmethod
    def append_replication(self, node: NodeInfo, key: InfoKey, value: bytes, current_index: int) -> bool:
        pass

    @abstractmethod
    def edit_value(self, node: NodeInfo, key: InfoKey, index: int, new_value: bytes) -> bool:
        pass
