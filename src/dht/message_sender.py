import random
from typing import List, Optional
from src.dht.node_info import NodeInfo
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData


# Stores all nodes, makes direct function call to a node, instead of sending message over TCP
class MessageSender:
    def __init__(self, module: int):
        self.module = module
        self.nodes = dict()

        # Just for testing
        self.successors = [None] * module

        self.message_counter = 0

    def ping(self, node: NodeInfo) -> bool:
        if node.node_id not in self.nodes.keys():
            return False
        self.message_counter += 1
        return node.node_id in self.nodes.keys()

    def notify_node(self, node: NodeInfo, possible_predecessor: NodeInfo) -> None:
        if node.node_id not in self.nodes.keys():
            return
        self.message_counter += 1
        self.nodes[node.node_id].update_previous_node(possible_predecessor)

    def request_successor(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].find_successor(target_id)

    def request_next_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].get_next_node()

    def request_previous_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].get_previous_node()

    def request_preceding_finger(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].find_preceding_finger(target_id)

    def request_successor_list(self, node: NodeInfo) -> Optional[List[NodeInfo]]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].get_successor_list()

    def propose_finger_update(self, node: NodeInfo, node_to_update: NodeInfo, finger_number: int) -> None:
        if node.node_id not in self.nodes.keys():
            return
        self.message_counter += 1
        self.nodes[node.node_id].propose_finger_update(node_to_update, finger_number)

    def propose_predecessor(self, node: NodeInfo, node_to_propose: NodeInfo) -> None:
        if node.node_id not in self.nodes.keys():
            return
        self.message_counter += 1
        self.nodes[node.node_id].update_previous_node(node_to_propose)

    def request_replication_info(self, node: NodeInfo) -> Optional[ReplicationInfo]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].get_replication_info()

    def request_data_by_keys(self, node: NodeInfo, keys: List[InfoKey]) -> Optional[ReplicationData]:
        if node.node_id not in self.nodes.keys():
            return None
        self.message_counter += 1
        return self.nodes[node.node_id].get_data_by_keys(keys)

    def update_replication_info(self, node: NodeInfo, new_info: ReplicationInfo) -> None:
        if node.node_id not in self.nodes.keys():
            return
        self.message_counter += 1
        return self.nodes[node.node_id].update_replication_info(new_info)

    def update_replication(self, node: NodeInfo, new_info: ReplicationInfo, new_data: ReplicationData) -> None:
        if node.node_id not in self.nodes.keys():
            return
        self.message_counter += 1
        return self.nodes[node.node_id].update_replication(new_info, new_data)

    # Returns node, such that node.id >= target_id, used just for validating result in simulator
    def get_real_successor(self, target_id) -> NodeInfo:
        return self.successors[(target_id - 1) % self.module].node_info

    def clear_message_counter(self) -> None:
        self.message_counter = 0

    def get_message_counter(self) -> int:
        return self.message_counter

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
        while self.successors[current_id].node_info.node_id == node_id:
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