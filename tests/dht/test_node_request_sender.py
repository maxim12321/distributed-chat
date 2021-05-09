import random
from copy import deepcopy
from typing import List, Optional, Dict

from src.dht.chord_node import ChordNode
from src.dht.node_info import NodeInfo
from src.dht.node_request_sender import NodeRequestSender
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


class TestNodeRequestSender(NodeRequestSender):
    def __init__(self, module: int):
        self.module = module
        self.nodes: Dict[int, ChordNode] = dict()

        self.successors: List[Optional[ChordNode]] = [None] * module

    def ping(self, node: NodeInfo) -> bool:
        return node.node_id in self.nodes.keys()

    def request_successor(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].find_successor(target_id))

    def request_next_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].get_next_node())

    def request_previous_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].get_previous_node())

    def request_preceding_finger(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].find_preceding_finger(target_id))

    def request_successor_list(self, node: NodeInfo) -> Optional[List[NodeInfo]]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].get_successor_list())

    def propose_finger_update(self, node: NodeInfo, node_to_update: NodeInfo, finger_number: int) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        self.nodes[node.node_id].propose_finger_update(deepcopy(node_to_update), finger_number)
        return b''

    def propose_predecessor(self, node: NodeInfo, node_to_propose: NodeInfo) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        self.nodes[node.node_id].update_previous_node(deepcopy(node_to_propose))
        return b''

    def request_replication_info(self, node: NodeInfo) -> Optional[ReplicationInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].get_replication_info())

    def request_data_by_keys(self, node: NodeInfo, keys: List[InfoKey]) -> Optional[ReplicationData]:
        if node.node_id not in self.nodes.keys():
            return None
        return deepcopy(self.nodes[node.node_id].get_data_by_keys(deepcopy(keys)))

    def update_replication_info(self, node: NodeInfo, new_info: ReplicationInfo) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        self.nodes[node.node_id].update_replication_info(deepcopy(new_info))
        return b''

    def update_replication(self, node: NodeInfo,
                           new_info: ReplicationInfo, new_data: ReplicationData) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        self.nodes[node.node_id].update_replication(deepcopy(new_info), deepcopy(new_data))
        return b''

    def get_value(self, node: NodeInfo, key: InfoKey) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        return self.nodes[node.node_id].get_value(key)

    def get_all_values(self, node: NodeInfo, key: InfoKey) -> Optional[List[bytes]]:
        if node.node_id not in self.nodes.keys():
            return None
        return self.nodes[node.node_id].get_all_values(key)

    def set_value(self, node: NodeInfo, key: InfoKey, value: bytes) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        self.nodes[node.node_id].set_value(key, value)
        return b''

    def append_value(self, node: NodeInfo, key: InfoKey, value: bytes) -> Optional[bytes]:
        if node.node_id not in self.nodes.keys():
            return None
        self.nodes[node.node_id].append_value(key, value)
        return b''

    # Returns node, such that node.id >= target_id, used just for validating result in simulator
    def get_real_successor(self, target_id) -> NodeInfo:
        return self.successors[(target_id - 1) % self.module].node_info

    def add_node(self, node_id: int, node) -> None:
        random_node = None
        if len(self.nodes) > 0:
            random_node = self.nodes[random.choice(list(self.nodes.keys()))].get_node_info()

        self.nodes[node_id] = node

        node.join(random_node)

        self._set_successors(node_id, node)

    def remove_node(self, node_id: int) -> None:
        self.nodes.pop(node_id)

        current_id = (node_id - 1) % self.module
        while current_id != node_id and self.successors[current_id].node_info.node_id == node_id:
            self.successors[current_id] = self.successors[node_id]
            current_id = (current_id - 1) % self.module

    def _set_successors(self, node_id: int, node) -> None:
        node_id = (node_id - 1) % self.module
        self.successors[node_id] = node

        while node_id not in self.nodes.keys():
            node_id = (node_id - 1) % self.module
            self.successors[node_id] = node

    def check_finger_tables(self) -> bool:
        for node in self.nodes.values():
            if not self._check_finger_table(node.get_finger_table()):
                print(f"----------- Error in finger_table of {node.node_info.node_id} -----------")
                return False
        return True

    def _check_finger_table(self, finger_table) -> bool:
        for finger in finger_table:
            successor = self.get_real_successor(finger.start)
            if successor.node_id != finger.node.node_id:
                print(f"(>= {finger.start}) should be {successor.node_id}, but {finger.node.node_id} found")
                return False
        return True
