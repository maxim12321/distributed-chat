from typing import List, Optional, Tuple

from src import constants
from src.dht.node_info import NodeInfo
from src.dht.node_request_sender import NodeRequestSender
from src.dht.finger import Finger
from src.replication.info_key import InfoKey
from src.replication.replication_info import ReplicationInfo
from src.replication.replication_data import ReplicationData
from src.replication.replication_manager import ReplicationManager


class ChordNode:
    def __init__(self, id_bit_length: int, node_id: int, node_ip: bytes, node_port: int,
                 request_sender: NodeRequestSender) -> None:
        self.id_bit_length = id_bit_length
        self.module = 2 ** id_bit_length
        self.node_info = NodeInfo(node_id, node_ip, node_port)
        self.request_sender = request_sender

        self.successor: NodeInfo = self.node_info
        self.predecessor: NodeInfo = self.node_info
        self.finger_table: List[Finger] = list()

        self.successor_list: List[NodeInfo] = list()

        self.last_updated_finger = 1

        self.replication_manager = ReplicationManager()

    def get_single_data_by_key(self, key: InfoKey) -> Optional[bytes]:
        data_successor = self.find_successor(key.data_id)
        return self.request_sender.get_value(data_successor, key)

    def get_all_data_by_key(self, key: InfoKey) -> Optional[List[bytes]]:
        data_successor = self.find_successor(key.data_id)
        return self.request_sender.get_all_values(data_successor, key)

    def set_value_by_key(self, key: InfoKey, value: bytes) -> None:
        data_successor = self.find_successor(key.data_id)
        self.request_sender.set_value(data_successor, key, value)

    def append_value_by_key(self, key: InfoKey, value: bytes) -> None:
        data_successor = self.find_successor(key.data_id)
        self.request_sender.append_value(data_successor, key, value)

    # Just for testing
    def get_node_info(self) -> NodeInfo:
        return self.node_info

    # Just for validating finger tables
    def get_finger_table(self) -> List[Finger]:
        return self.finger_table

    def get_next_node(self) -> NodeInfo:
        self._check_successor()
        return self.successor

    def get_previous_node(self) -> NodeInfo:
        self._check_predecessor()
        return self.predecessor

    def get_replication_info(self) -> ReplicationInfo:
        return self.replication_manager.get_info()

    def get_data_by_keys(self, keys: List[InfoKey]) -> ReplicationData:
        return self.replication_manager.get_data_by_keys(keys)

    def get_value(self, key: InfoKey) -> Optional[bytes]:
        return self.replication_manager.get_single_data(key)

    def get_all_values(self, key: InfoKey) -> Optional[List[bytes]]:
        return self.replication_manager.get_data(key)

    def set_value(self, key: InfoKey, value: bytes) -> None:
        self.replication_manager.set_data(self.node_info.node_id, key, value)
        self._push_key_replication(key)

    def append_value(self, key: InfoKey, value: bytes) -> None:
        self.replication_manager.append_data(self.node_info.node_id, key, value)
        self._push_key_replication(key)

    # Finds replication for a given key and pushes updates to the successor
    def _push_key_replication(self, key: InfoKey) -> None:
        info, data = self.replication_manager.get_key_replication(key)
        info_to_push = info.get_decremented_info()

        self.request_sender.update_replication(self.get_next_node(), info_to_push, data)

    # Update current replication info, decrease values, push info to the successor
    def update_replication_info(self, new_info: ReplicationInfo) -> None:
        new_info = self.replication_manager.update_replication_info(self.node_info.node_id, new_info)
        info_to_push = new_info.get_decremented_info()

        if info_to_push.get_size() > 0:
            self.request_sender.update_replication_info(self.get_next_node(), info_to_push)

    # Update replication info and data, decrease values, push to the successor
    def update_replication(self, new_info: ReplicationInfo, new_data: ReplicationData) -> None:
        new_info, new_data = self.replication_manager.update_replication(self.node_info.node_id, new_info, new_data)
        info_to_push = new_info.get_decremented_info()

        if info_to_push.get_size() > 0:
            self.request_sender.update_replication(self.get_next_node(), info_to_push, new_data)

    # possible_predecessor is proposed as a self.predecessor
    def update_previous_node(self, possible_predecessor: NodeInfo) -> None:
        self._check_predecessor()

        # If self has no predecessor, update it
        if self.predecessor.node_id == self.node_info.node_id:
            self._set_predecessor(possible_predecessor)

        # If possible predecessor is better than current one, update it
        if self.is_inside_right(self.predecessor.node_id, self.node_info.node_id, possible_predecessor.node_id):
            self._set_predecessor(possible_predecessor)

    def get_successor_list(self) -> List[NodeInfo]:
        return self.successor_list

    def join(self, other_node: Optional[NodeInfo]) -> None:
        self._fill_fingers_with_self()
        if other_node is None:
            return

        successor = self.request_sender.request_successor(other_node, self.node_info.node_id)
        self._init_finger_table(successor)
        self._update_successor_list()
        self._update_other_nodes()
        self._replicate_from_successor()
        self._update_replication_from_predecessor()

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
        if self.last_updated_finger == self.id_bit_length:
            self.last_updated_finger = 1

    # Tries to update successor from current successor's predecessor
    def _check_possible_successor(self) -> None:
        possible_successor = self.request_sender.request_previous_node(self.successor)

        if self.is_inside_right(self.node_info.node_id, self.successor.node_id, possible_successor.node_id):
            if possible_successor.node_id != self.successor.node_id:
                self._set_successor(possible_successor)
                self._check_possible_successor()

        self.request_sender.propose_predecessor(self.successor, self.node_info)

    # If successor failed, finds nearest new successor and updates successor list
    def _check_successor(self) -> None:
        if self.request_sender.ping(self.successor):
            return

        for successor in self.successor_list:
            if self.request_sender.ping(successor):
                self._set_successor(successor)
                self._check_possible_successor()
                self._update_successor_list()
                self.request_sender.propose_predecessor(successor, self.node_info)
                return

        self._set_successor(self.node_info)

    # Can be called when successor is correct and alive
    def _update_successor_list(self) -> None:
        next_list = self.request_sender.request_successor_list(self.successor)

        if len(next_list) == constants.SUCCESSOR_LIST_SIZE:
            next_list = next_list[:-1]

        self.successor_list = [self.successor]
        self.successor_list.extend(next_list)

    # If predecessor failed, sets self as a predecessor
    def _check_predecessor(self) -> None:
        if self.predecessor.node_id == self.successor.node_id:
            return

        if not self.request_sender.ping(self.predecessor):
            self._set_predecessor(self.node_info)

    # Initializes successor, predecessor and finger_table: creates segments [begin; end) = [id + 2^i; id + 2^{i+1})
    def _fill_fingers_with_self(self) -> None:
        start = (self.node_info.node_id + 1) % self.module
        finger_length = 1

        for i in range(self.id_bit_length):
            end = (start + finger_length) % self.module

            self.finger_table.append(Finger(start, end, self.node_info))

            start = end
            finger_length *= 2

        self._set_successor(self.node_info)
        self._set_predecessor(self.node_info)

    # For i-th finger, finds last node, such that self can be i-th finger of this node
    def _update_other_nodes(self) -> None:
        for i in range(self.id_bit_length):
            # for i in range(1):
            predecessor, _ = self._find_predecessor((self.node_info.node_id - 2 ** i) % self.module)
            self.request_sender.propose_finger_update(predecessor, self.node_info, i)

    # If node is finger_number's finger, update finger and propose same finger for our predecessor
    def propose_finger_update(self, node: NodeInfo, finger_number: int) -> None:
        old_finger: NodeInfo = self.finger_table[finger_number].node

        # start = node_id <= end, cannot make better
        if self.finger_table[finger_number].start == old_finger.node_id:
            return

        if self.is_inside_left(self.finger_table[finger_number].start, old_finger.node_id, node.node_id):
            if finger_number == 0:
                self._set_successor(node)
            else:
                self.finger_table[finger_number].node = node

            # TODO: Try to send only when it can possibly be
            self.request_sender.propose_finger_update(self.predecessor, node, finger_number)

    # Sets fingers, assuming that successor is self.successor in the ring
    def _init_finger_table(self, successor: NodeInfo) -> None:
        self._set_successor(successor)

        last_successor_id = successor.node_id
        for i in range(1, self.id_bit_length):
            if self.is_inside_right(self.node_info.node_id, last_successor_id, self.finger_table[i].start):
                # If (i-1)-th finger is also i-th finger, no need to make request
                self.finger_table[i].node = self.finger_table[i - 1].node
            else:
                # Get real successors from chord ring
                target_id = (self.finger_table[i].start - 1) % self.module
                self.finger_table[i].node = self.request_sender.request_successor(successor, target_id)

            last_successor_id = self.finger_table[i].node.node_id

        self._set_predecessor(self.request_sender.request_previous_node(successor))
        self.request_sender.propose_finger_update(self.predecessor, self.node_info, 0)

        self.request_sender.propose_predecessor(successor, self.node_info)

    # Gets data to replicate from a successor, supposing self.successor is alive and correct, and updates successor info
    def _replicate_from_successor(self) -> None:
        self._check_successor()

        replication_info = self.request_sender.request_replication_info(self.successor)

        # Remove successor's replication, for that self is not a successor
        keys_to_remove = replication_info.get_keys_with_id_inside(self.node_info.node_id, self.successor.node_id)
        replication_info.remove_keys(keys_to_remove)

        if replication_info.get_size() == 0:
            return

        # Get data, associated with appropriate keys
        replication_data = self.request_sender.request_data_by_keys(self.get_next_node(), replication_info.get_keys())

        # Set info and data, update values, for that self became first node
        self.replication_manager.set_replication(replication_info, replication_data)
        self.replication_manager.update_first_nodes(self.node_info.node_id)

        # Decrease keys and push info updates to the successors
        new_info = replication_info.get_decremented_info()
        self.request_sender.update_replication_info(self.successor, new_info)

    # Returns node: NodeInfo, such that node.id < target_id <= node.successor.id
    def find_successor(self, target_id: int) -> NodeInfo:
        # self.stabilize()
        # self._check_possible_successor()
        self._check_successor()
        self._update_successor_list()
        # self._check_predecessor()

        _, successor = self._find_predecessor(target_id)
        return successor

    # Returns node: NodeInfo, such that node.id <= target_id < node.successor.id
    def _find_predecessor(self, target_id: int) -> Tuple[NodeInfo, NodeInfo]:
        node = self.node_info
        node_successor = self.get_next_node()

        while not self.is_inside_left(node.node_id, node_successor.node_id, target_id):
            node = self.request_sender.request_preceding_finger(node, target_id)
            node_successor = self.request_sender.request_next_node(node)

        return node, node_successor

    # Returns farthest node: NodeInfo **from finger_table**, such that id < node.id <= target_id
    def find_preceding_finger(self, target_id: int) -> NodeInfo:
        for finger in reversed(self.finger_table):
            if not self.request_sender.ping(finger.node):
                continue

            if self.is_inside_right(self.node_info.node_id, target_id, finger.node.node_id):
                return finger.node

        return self.node_info

    def _set_successor(self, successor: NodeInfo) -> None:
        self.successor = successor
        self.finger_table[0].node = successor

    # Sets predecessor and updates replication, if needed
    def _set_predecessor(self, predecessor: NodeInfo) -> None:
        # If predecessor is not better (predecessor failed), update replication info for data from predecessor
        if not self.is_inside_left(self.predecessor.node_id, self.node_info.node_id, predecessor.node_id):
            info, data = self.replication_manager.move_all_from_predecessor(self.node_info.node_id)

            if info.get_size() > 0:
                info_to_push = info.get_decremented_info()
                self.request_sender.update_replication(self.get_next_node(), info_to_push, data)

        self.predecessor = predecessor

        if predecessor.node_id != self.node_info.node_id:
            self._update_replication_from_predecessor()

    # Requests replication data from successor, pushes updates to the successor
    def _update_replication_from_predecessor(self) -> None:
        if self.predecessor.node_id == self.node_info.node_id:
            return

        replication_info = self.request_sender.request_replication_info(self.predecessor)

        # Remove overlapping and unnecessary keys, decrease values from predecessor
        updated_info = self.replication_manager.update_replication_info(self.node_info.node_id, replication_info)
        updated_info.decrement_values()

        # Remove keys for data that shouldn't be stored
        keys_to_remove = updated_info.get_keys_to_remove()
        updated_info.remove_keys(keys_to_remove)

        if updated_info.get_size() == 0:
            return

        # Request data for appropriate keys from the predecessor
        replication_data = self.request_sender.request_data_by_keys(self.predecessor, updated_info.get_keys())
        self.replication_manager.update_replication_data(replication_data)

        # Decrease keys and push data updates to the successors
        info_to_push = updated_info.get_decremented_info()
        self.request_sender.update_replication(self.get_next_node(), info_to_push, replication_data)

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
