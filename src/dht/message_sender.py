import random
from src.dht.node_info import NodeInfo


# Stores all nodes, makes direct function call to a node, instead of sending message over TCP
class MessageSender:
    def __init__(self, module: int):
        self.module = module
        self.nodes = dict()

        # Just for testing
        self.successors = [None] * module

    def request_successor(self, node: NodeInfo, target_id: int) -> NodeInfo:
        return self.nodes[node.node_id].find_successor(target_id)

    def request_next_node(self, node: NodeInfo) -> NodeInfo:
        return self.nodes[node.node_id].get_next_node()

    def request_previous_node(self, node: NodeInfo) -> NodeInfo:
        return self.nodes[node.node_id].get_previous_node()

    def request_preceding_finger(self, node: NodeInfo, target_id: int) -> NodeInfo:
        return self.nodes[node.node_id].find_preceding_finger(target_id)

    def propose_finger_update(self, node: NodeInfo, node_to_update: NodeInfo, finger_number: int) -> None:
        self.nodes[node.node_id].propose_finger_update(node_to_update, finger_number)

    def propose_predecessor(self, node: NodeInfo, node_to_propose: NodeInfo) -> None:
        self.nodes[node.node_id].set_previous_node(node_to_propose)

    def add_node(self, node_id: int, node) -> None:
        random_node = None
        if len(self.nodes) > 0:
            random_node = self.nodes[random.choice(list(self.nodes.keys()))].get_node_info()

        self.nodes[node_id] = node

        print("Trying to join")
        print(random_node)
        node.join(random_node)

        self._set_successors(node_id, node)

    # Returns node, such that node.id >= target_id, used just for validating result in simulator
    def get_real_successor(self, target_id) -> NodeInfo:
        return self.successors[(target_id - 1) % self.module].node_info

    def _set_successors(self, node_id: int, node):
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
