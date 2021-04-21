from typing import List, Optional
from src.dht.node_info import NodeInfo
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


class MessageSender:
    def ping(self, node: NodeInfo) -> bool:
        pass

    def request_successor(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        # return node.find_successor(target_id)
        pass

    def request_next_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        # return node.get_next_node()
        pass

    def request_previous_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        # return node.get_previous_node()
        pass

    def request_preceding_finger(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        # return node.find_preceding_finger(target_id)
        pass

    def request_successor_list(self, node: NodeInfo) -> Optional[List[NodeInfo]]:
        # return node.get_successor_list()
        pass

    def propose_finger_update(self, node: NodeInfo, node_to_update: NodeInfo, finger_number: int) -> None:
        # node.propose_finger_update(node_to_update, finger_number)
        pass

    def propose_predecessor(self, node: NodeInfo, node_to_propose: NodeInfo) -> None:
        # node.update_previous_node(node_to_propose)
        pass

    def request_replication_info(self, node: NodeInfo) -> Optional[ReplicationInfo]:
        # return node.get_replication_info()
        pass

    def request_data_by_keys(self, node: NodeInfo, keys: List[InfoKey]) -> Optional[ReplicationData]:
        # return node.get_data_by_keys(keys)
        pass

    def update_replication_info(self, node: NodeInfo, new_info: ReplicationInfo) -> None:
        # return node.update_replication_info(new_info)
        pass

    def update_replication(self, node: NodeInfo, new_info: ReplicationInfo, new_data: ReplicationData) -> None:
        # return node.update_replication(new_info, new_data)
        pass
