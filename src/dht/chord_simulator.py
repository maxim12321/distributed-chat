import os
import random
from typing import Dict, List, Optional
from src.dht.chord_node import ChordNode
from src.dht.message_sender import MessageSender
from src.replication.info_key import InfoKey


class ChordSimulator:
    def __init__(self, id_power):
        self.m = id_power
        self.module = 2 ** self.m
        self.nodes: Dict[int, ChordNode] = dict()
        self.message_sender = MessageSender(self.module)

        self.max_messages_sent = 0
        self.total_messages_sent = 0
        self.requests_count = 0

        self.max_adding_sent = 0
        self.total_adding_sent = 0
        self.total_adds = 0

        self.max_removing_sent = 0
        self.total_removing_sent = 0
        self.total_removes = 0

        self.max_data_update_sent = 0
        self.total_data_update_sent = 0
        self.total_data_updates = 0

        self.stored_data: Dict[InfoKey, List[bytes]] = dict()

    def _update_message_stats(self):
        messages_sent: int = self.message_sender.get_message_counter()
        self.max_messages_sent = max(self.max_messages_sent, messages_sent)
        self.total_messages_sent += messages_sent
        self.requests_count += 1

    def _update_adding_stats(self):
        messages_sent: int = self.message_sender.get_message_counter()
        self.max_adding_sent = max(self.max_adding_sent, messages_sent)
        self.total_adding_sent += messages_sent
        self.total_adds += 1

    def _update_removing_stats(self):
        messages_sent: int = self.message_sender.get_message_counter()
        self.max_removing_sent = max(self.max_removing_sent, messages_sent)
        self.total_removing_sent += messages_sent
        self.total_removes += 1

    def _update_data_stats(self):
        messages_sent: int = self.message_sender.get_message_counter()
        self.max_data_update_sent = max(self.max_data_update_sent, messages_sent)
        self.total_data_update_sent += messages_sent
        self.total_data_updates += 1

    def add_random_node(self) -> None:
        node_id = random.randint(0, self.module - 1)
        while node_id in self.nodes.keys():
            node_id = random.randint(0, self.module - 1)

        print(f"Adding {node_id} node")

        chord_node = ChordNode(self.m, node_id, self.message_sender)

        self.nodes[node_id] = chord_node

        self.message_sender.clear_message_counter()
        self.message_sender.add_node(node_id, chord_node)
        self._update_adding_stats()

    def remove_random_node(self) -> None:
        node_id = random.choice(list(self.nodes.keys()))
        self.nodes.pop(node_id)
        print(f"Node {node_id} removed\n")

        self.message_sender.clear_message_counter()
        self.message_sender.remove_node(node_id)
        self._update_removing_stats()

    def set_value(self, key: InfoKey, value: bytes) -> None:
        print(f"Setting {key}'s value")
        target_node = self._get_successor(key.data_id)

        self.message_sender.clear_message_counter()
        target_node.set_value(key, value)
        self._update_data_stats()

        self.stored_data[key] = [value]

    def append_value(self, key: InfoKey, value: bytes) -> None:
        print(f"Appending {key}'s value")
        target_node = self._get_successor(key.data_id)

        self.message_sender.clear_message_counter()
        target_node.append_value(key, value)
        self._update_data_stats()

        if key not in self.stored_data.keys():
            self.stored_data[key] = list()
        self.stored_data[key].append(value)

    def get_value(self, key: InfoKey) -> Optional[bytes]:
        target_node = self._get_successor(key.data_id)

        self.message_sender.clear_message_counter()
        value = target_node.get_value(key)
        self._update_data_stats()
        return value

    def get_all_values(self, key: InfoKey) -> Optional[List[bytes]]:
        target_node = self._get_successor(key.data_id)

        self.message_sender.clear_message_counter()
        values = target_node.get_all_values(key)
        self._update_data_stats()
        return values

    def _get_successor(self, target_id: int) -> ChordNode:
        node_id = random.choice(list(self.nodes.keys()))

        self.message_sender.clear_message_counter()
        successor = self.nodes[self.nodes[node_id].find_successor(target_id).node_id]
        self._update_message_stats()
        return successor

    def count_replicas(self, key: InfoKey) -> int:
        count = 0

        for node in self.nodes.values():
            if node.get_value(key) is not None:
                count += 1

        return count

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

    def check_random_value(self) -> None:
        random_key: InfoKey = random.choice(list(self.stored_data.keys()))
        self.check_value(random_key)

    def check_value(self, key: InfoKey) -> None:
        print(f"Checking key {key}:")

        if self.count_replicas(key) != 5 or self.get_replication_coefficients(key) != [1, 2, 3, 4, 5]:
            # Make some stabilization and try again
            node = self._get_successor(key.data_id)
            for i in range(5):
                node.stabilize()
                node = self.nodes[node.get_next_node().node_id]

        if self.count_replicas(key) != 5 or self.get_replication_coefficients(key) != [1, 2, 3, 4, 5]:
            print(f"Error! Replicas: {self.count_replicas(key)}")

            print(f"{self._get_successor(key.data_id).node_info.node_id} successors:"
                  f"{self._get_successor(key.data_id).successor_list}")
            exit(0)

        values = self.get_all_values(key)
        if values == self.stored_data[key]:
            print("OK")
        else:
            print(f"ERROR! Got {values}, but {self.stored_data[key]} expected")
            exit(0)

    def get_replication_coefficients(self, key: InfoKey) -> List[int]:
        values: List[int] = list()
        for node in self.nodes.values():
            if node.get_value(key) is not None:
                values.append(node.replication_manager.get_info().get_value(key))
        return sorted(values)

    def check_random_node(self) -> None:
        node_id: int = random.choice(list(self.nodes.keys()))
        print(f"Checking {node_id}:")
        target_id: int = random.randint(0, self.module - 1)

        self.message_sender.clear_message_counter()
        successor = self.message_sender.request_successor(self.nodes[node_id].get_node_info(), target_id)
        self._update_message_stats()

        real_successor = self.message_sender.get_real_successor((target_id + 1) % self.module)

        print(f"Searching for successor of id={target_id}...")
        print(f"It took {self.message_sender.get_message_counter()} messages to find successor")
        if successor == real_successor:
            print("OK\n")
        else:
            print(f"Incorrect! Got id={successor.node_id}, but id={real_successor.node_id} expected")
            exit(0)

    def check_all_node_fingers(self) -> None:
        if not self.message_sender.check_finger_tables():
            self.print_nodes()
            exit(0)

    def print_statistics(self) -> None:
        print("--------------- LOOKUP ---------------")
        self._print_statistics(self.requests_count, self.max_messages_sent, self.total_messages_sent)

        print("--------------- ADDING ---------------")
        self._print_statistics(self.total_adds, self.max_adding_sent, self.total_adding_sent)

        print("--------------- REMOVE ---------------")
        self._print_statistics(self.total_removes, self.max_removing_sent, self.total_removing_sent)

        print("---------------- DATA ----------------")
        self._print_statistics(self.total_data_updates, self.max_data_update_sent, self.total_data_update_sent)

    @staticmethod
    def _print_statistics(counter: int, max_value: int, total_value: int):
        print(f"Total requests made: {counter}")
        print(f"Maximum number of messages per request: {max_value}")
        print(f"Average number of messages per request: {total_value / counter}")
        print()

    def print_nodes(self) -> None:
        print(f"Chord ({len(self.nodes)} nodes):")
        for node_id in self.nodes:
            print(f"-- (ID = {node_id}): {self.nodes[node_id]}")
        print()
