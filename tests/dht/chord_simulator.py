import os
import random
from typing import Dict, List, Optional

from src import constants
from src.dht.chord_node import ChordNode
from src.replication.info_key import InfoKey
from tests.dht.test_node_request_sender import TestNodeRequestSender


class ChordSimulator:
    def __init__(self, id_power) -> None:
        self.id_bit_length = id_power
        self.module = 2 ** self.id_bit_length

        self.nodes: Dict[int, ChordNode] = dict()
        self.request_sender: TestNodeRequestSender = TestNodeRequestSender(self.module)

        self.stored_data: Dict[InfoKey, List[bytes]] = dict()

    def add_random_node(self) -> None:
        node_id = random.randint(0, self.module - 1)
        while node_id in self.nodes.keys():
            node_id = random.randint(0, self.module - 1)

        self.add_node(node_id)

    def add_node(self, node_id: int) -> None:
        chord_node = ChordNode(self.id_bit_length, node_id, b'0', 0, self.request_sender)

        self.nodes[node_id] = chord_node
        self.request_sender.add_node(node_id, chord_node)

    def remove_random_node(self) -> None:
        node_id = random.choice(list(self.nodes.keys()))
        self.nodes.pop(node_id)

        self.remove_node(node_id)

    def remove_node(self, node_id: int) -> None:
        self.request_sender.remove_node(node_id)

    def set_value(self, key: InfoKey, value: bytes) -> None:
        target_node = self._get_successor(key.data_id)

        target_node.set_value(key, value)

        self.stored_data[key] = [value]

    def append_value(self, key: InfoKey, value: bytes) -> None:
        target_node = self._get_successor(key.data_id)

        target_node.append_value(key, value)

        if key not in self.stored_data.keys():
            self.stored_data[key] = list()
        self.stored_data[key].append(value)

    def edit_value(self, key: InfoKey, index: int, new_value: bytes) -> None:
        target_node = self._get_successor(key.data_id)

        target_node.edit_value(key, index, new_value)

        self.stored_data[key][index] = new_value

    def get_value(self, key: InfoKey) -> Optional[bytes]:
        target_node = self._get_successor(key.data_id)

        return target_node.get_value(key)

    def get_all_values(self, key: InfoKey) -> Optional[List[bytes]]:
        target_node = self._get_successor(key.data_id)

        return target_node.get_all_values(key)

    def _get_successor(self, target_id: int) -> ChordNode:
        node_id = random.choice(list(self.nodes.keys()))
        return self.nodes[self.nodes[node_id].find_successor(target_id).node_id]

    def count_replicas(self, key: InfoKey) -> int:
        count = 0
        for node in self.nodes.values():
            if node.get_value(key) is not None:
                count += 1

        return count

    def get_nodes_replicating_key(self, key: InfoKey) -> List[ChordNode]:
        nodes: List[ChordNode] = list()
        for node in self.nodes.values():
            if node.get_value(key) is not None:
                nodes.append(node)
        return nodes

    def set_random_value(self) -> InfoKey:
        random_key = InfoKey(random.randint(0, 1000), random.randint(0, self.module - 1))
        random_value = os.urandom(10)

        self.set_value(random_key, random_value)
        return random_key

    def append_random_value(self) -> InfoKey:
        random_key = InfoKey(random.randint(0, 1000), random.randint(0, self.module - 1))
        random_value = os.urandom(10)
        self.append_value(random_key, random_value)
        return random_key

    def edit_random_value(self, key: InfoKey) -> None:
        random_index = random.randrange(0, len(self.stored_data[key]))
        random_value = os.urandom(10)
        self.edit_value(key, random_index, random_value)

    def check_random_value(self) -> bool:
        random_key: InfoKey = random.choice(list(self.stored_data.keys()))
        return self.check_value(random_key)

    def check_value(self, key: InfoKey) -> bool:
        target_replication: List[int] = [i for i in range(1, constants.REPLICATION_FACTOR + 1)]

        if self.count_replicas(key) != constants.REPLICATION_FACTOR \
                or self.get_replication_coefficients(key) != target_replication:
            # Make some stabilization and try again
            node = self._get_successor(key.data_id)
            for i in range(constants.REPLICATION_FACTOR):
                node.check_possible_successor()
                node.update_successor_list()
                for _ in range(self.id_bit_length):
                    node.fix_finger()
                node = self.nodes[node.get_next_node().node_id]

        if self.count_replicas(key) != constants.REPLICATION_FACTOR \
                or self.get_replication_coefficients(key) != target_replication:
            print(f"Error! Replicas: {self.count_replicas(key)}")
            print(self.get_replication_coefficients(key))

            self.print_replication()

            print(f"\nKey {key} replication:")
            for node in self.get_nodes_replicating_key(key):
                print(f"Node {node.node_info.node_id} replica: {node.get_replication_info().get_info_by_keys([key])}")

            print(f"{self._get_successor(key.data_id).node_info.node_id} successors:"
                  f"{self._get_successor(key.data_id).successor_list}")
            return False

        for node in self.get_nodes_replicating_key(key):
            values = node.get_all_values(key)
            if values != self.stored_data[key]:
                print(f"ERROR! Got {values}, but {self.stored_data[key]} expected")
                print(f"\nKey {key} replication:")
                for replicating_node in self.get_nodes_replicating_key(key):
                    print(f"Node {replicating_node.node_info.node_id} replica: "
                          f"{replicating_node.replication_manager.get_data(key)}")
                return False

        return True

    def get_replication_coefficients(self, key: InfoKey) -> List[int]:
        values: List[int] = list()
        for node in self.nodes.values():
            if node.get_value(key) is not None:
                values.append(node.replication_manager.get_info().get_value(key).current_index)
        return sorted(values)

    def check_random_node(self) -> bool:
        node_id: int = random.choice(list(self.nodes.keys()))
        target_id: int = random.randint(0, self.module - 1)

        successor = self.request_sender.request_successor(self.nodes[node_id].get_node_info(), target_id)

        real_successor = self.request_sender.get_real_successor((target_id + 1) % self.module)

        if successor.node_id != real_successor.node_id:
            print(f"Incorrect! Got id={successor.node_id}, but id={real_successor.node_id} expected")
            return False

        return True

    def check_node_successors(self) -> bool:
        for node in self.nodes.values():
            next_id = (node.node_info.node_id + 1) % self.module
            next_node = self.request_sender.get_real_successor(next_id)

            if node.get_next_node().node_id != next_node.node_id:
                print(f"{node.node_info.node_id}'s successor is incorrect! Got {node.successor.node_id}, "
                      f"but {next_node.node_id} expected")
                return False
        return True

    def check_node_predecessors(self) -> bool:
        for node in self.nodes.values():
            next_id = self.request_sender.get_real_successor((node.node_info.node_id + 1) % self.module).node_id
            next_node = self.nodes[next_id]

            if next_node.get_previous_node().node_id != node.node_info.node_id:
                print(f"{next_id}'s predecessor is incorrect! Got {next_node.predecessor.node_id}, "
                      f"but {node.node_info.node_id} expected")
                return False
        return True

    def check_all_node_fingers(self) -> bool:
        if not self.request_sender.check_finger_tables():
            self.print_nodes()
            return False
        return True

    def print_nodes(self) -> None:
        print(f"Chord ({len(self.nodes)} nodes):")
        for node_id in self.nodes:
            print(f"-- (ID = {node_id}): {self.nodes[node_id]}")
        print()

    def print_replication(self) -> None:
        print(f"Chord ({len(self.nodes)} nodes) replication info:")
        for node_id in self.nodes:
            print(f"-- (ID = {node_id}): {self.nodes[node_id].get_replication_info()}")
