from src.dht.node_info import NodeInfo
from src.dht.message_sender import MessageSender
from src.dht.finger import Finger


class ChordNode:
    def __init__(self, m: int, node_id: int, message_sender: MessageSender):
        self.SUCCESSOR_LIST_SIZE = 5

        self.m = m
        self.module = 2 ** m
        self.node_info = NodeInfo(node_id)
        self.message_sender = message_sender

        self.successor: NodeInfo = None
        self.predecessor: NodeInfo = None
        self.finger_table = list()

        self.successor_list = list()

        self.last_updated_finger = 1

    # Temp, just for testing
    def get_node_info(self) -> NodeInfo:
        return self.node_info

    # Temp, just for validating finger tables
    def get_finger_table(self) -> list:
        return self.finger_table

    def get_next_node(self) -> NodeInfo:
        self._check_successor()
        return self.successor

    def get_previous_node(self) -> NodeInfo:
        self._check_predecessor()
        return self.predecessor

    def update_previous_node(self, possible_predecessor: NodeInfo) -> None:
        if self.predecessor.node_id == self.node_info.node_id:
            self.predecessor = possible_predecessor

        if self.is_inside_right(self.predecessor.node_id, self.node_info.node_id, possible_predecessor.node_id):
            self.predecessor = possible_predecessor

    def get_successor_list(self) -> list:
        return self.successor_list

    def join(self, other_node: NodeInfo) -> None:
        self._fill_fingers_with_self()
        if other_node is None:
            return

        successor = self.message_sender.request_successor(other_node, self.node_info.node_id)
        self._init_finger_table(successor)
        self._update_successor_list()
        self._update_other_nodes()

    # Should be called periodically, fixes predecessor and successors
    def stabilize(self) -> None:
        self._check_successor()
        self._check_possible_successor()

        self._update_successor_list()

        self._check_predecessor()

    # Should be called periodically, fixes one finger, needs m calls to fix all fingers
    def fix_finger(self) -> None:
        target_id = (self.finger_table[self.last_updated_finger].start - 1) % self.module
        self.finger_table[self.last_updated_finger].node = self.find_successor(target_id)

        self.last_updated_finger += 1
        if self.last_updated_finger == self.m:
            self.last_updated_finger = 1

    # Tries to update successor from current successor's predecessor
    def _check_possible_successor(self) -> None:
        possible_successor = self.message_sender.request_previous_node(self.successor)
        if self.is_inside_right(self.node_info.node_id, self.successor.node_id, possible_successor.node_id):
            self.successor = possible_successor
            self.finger_table[0].node = self.successor

        self.message_sender.propose_predecessor(self.successor, self.node_info)

    # If successor failed, finds nearest new successor and updates successor list
    def _check_successor(self) -> None:
        if self.message_sender.ping(self.successor):
            return

        for successor in self.successor_list:
            if self.message_sender.ping(successor):
                self.successor = successor
                self.finger_table[0].node = self.successor
                self._update_successor_list()
                return

        self.successor = self.node_info
        self.finger_table[0].node = self.successor

    # Can be called when successor is correct and alive
    def _update_successor_list(self) -> None:
        next_list = self.message_sender.request_successor_list(self.successor)

        if len(next_list) == self.SUCCESSOR_LIST_SIZE:
            next_list = next_list[:-1]

        self.successor_list = [self.successor]
        self.successor_list.extend(next_list)

    # If predecessor failed, sets self as a predecessor
    def _check_predecessor(self) -> None:
        if self.predecessor.node_id == self.successor.node_id:
            return

        if not self.message_sender.ping(self.predecessor):
            self.predecessor = self.node_info

    # Initializes successor, predecessor and finger_table: creates segments [begin; end) = [id + 2^i; id + 2^{i+1})
    def _fill_fingers_with_self(self) -> None:
        start = (self.node_info.node_id + 1) % self.module
        finger_length = 1

        for i in range(self.m):
            end: int = (start + finger_length) % self.module

            self.finger_table.append(Finger(start, end, self.node_info))

            start = (start + finger_length) % self.module
            finger_length *= 2

        self.successor = self.node_info
        self.predecessor = self.node_info

    # For i-th finger, finds last node, such that self can be i-th finger of this node
    def _update_other_nodes(self) -> None:
        for i in range(self.m):
            predecessor = self._find_predecessor((self.node_info.node_id - 2 ** i) % self.module)
            self.message_sender.propose_finger_update(predecessor, self.node_info, i)

    # If node is finger_number's finger, update finger and propose same finger for our predecessor
    def propose_finger_update(self, node: NodeInfo, finger_number: int) -> None:
        old_finger: NodeInfo = self.finger_table[finger_number].node

        # start = node_id <= end, cannot make better
        if self.finger_table[finger_number].start == old_finger.node_id:
            return

        if self.is_inside_left(self.finger_table[finger_number].start, old_finger.node_id, node.node_id):
            self.finger_table[finger_number].node = node
            self.successor = self.finger_table[0].node
            self.message_sender.propose_finger_update(self.predecessor, node, finger_number)

    # Sets fingers, assuming that successor is self.successor in the ring
    def _init_finger_table(self, successor: NodeInfo) -> None:
        self.successor = successor
        self.finger_table[0].node = successor

        last_successor_id = successor.node_id
        for i in range(1, self.m):
            if self.is_inside_right(self.node_info.node_id, last_successor_id, self.finger_table[i].start):
                # If (i-1)-th finger is also i-th finger, no need to make request
                self.finger_table[i].node = self.finger_table[i - 1].node
            else:
                # Get real successors from chord ring
                target_id = (self.finger_table[i].start - 1) % self.module
                self.finger_table[i].node = self.message_sender.request_successor(successor, target_id)

            last_successor_id = self.finger_table[i].node.node_id

        self.predecessor = self.message_sender.request_previous_node(successor)
        self.message_sender.propose_predecessor(successor, self.node_info)

    # Returns node: NodeInfo, such that node.id < target_id <= node.successor.id
    def find_successor(self, target_id: int) -> NodeInfo:
        self.stabilize()
        preceding_node: NodeInfo = self._find_predecessor(target_id)

        if preceding_node == self.node_info:
            return self.successor
        return self.message_sender.request_next_node(preceding_node)

    # Returns node: NodeInfo, such that node.id <= target_id < node.successor.id
    def _find_predecessor(self, target_id: int) -> NodeInfo:
        node = self.node_info
        node_successor = self.successor

        while not self.is_inside_left(node.node_id, node_successor.node_id, target_id):
            node = self.message_sender.request_preceding_finger(node, target_id)
            node_successor = self.message_sender.request_next_node(node)

        return node

    # Returns farthest node: NodeInfo **from finger_table**, such that id < node.id <= target_id
    def find_preceding_finger(self, target_id: int) -> NodeInfo:
        for finger in reversed(self.finger_table):
            if not self.message_sender.ping(finger.node):
                continue

            if self.is_inside_right(self.node_info.node_id, target_id, finger.node.node_id):
                return finger.node

        return self.node_info

    # Returns true, if left < value <= right; is_inside_right(x, x, a) -> True, 'cause (x; x] is whole circle
    @staticmethod
    def is_inside_right(left: int, right: int, value: int) -> bool:
        if left < right:
            return left < value <= right
        return value > left or value <= right

    # Returns true, if left <= value < right; is_inside_left(x, x, a) -> True, 'cause [x; x) is whole circle
    @staticmethod
    def is_inside_left(left: int, right: int, value: int) -> bool:
        if left < right:
            return left <= value < right
        return value >= left or value < right

    def __str__(self) -> str:
        fingers = ""
        for finger in self.finger_table:
            fingers += f"{finger.node.node_id} (>= {finger.start}), "
        return f"id={self.node_info.node_id}, prev:{self.predecessor.node_id}, fingers:{fingers}"
