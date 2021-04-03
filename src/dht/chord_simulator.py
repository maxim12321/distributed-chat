import random
from src.dht.chord_node import ChordNode
from src.dht.message_sender import MessageSender


class ChordSimulator:
    def __init__(self, id_power):
        self.m = id_power
        self.module = 2 ** self.m
        self.nodes = dict()
        self.message_sender = MessageSender(self.module)

        self.max_messages_sent = 0
        self.total_messages_sent = 0
        self.requests_count = 0

    def add_random_node(self) -> None:
        node_id = random.randint(0, self.module - 1)
        while node_id in self.nodes.keys():
            node_id = random.randint(0, self.module - 1)

        print(f"Adding {node_id} node")

        chord_node = ChordNode(self.m, node_id, self.message_sender)

        self.nodes[node_id] = chord_node
        self.message_sender.add_node(node_id, chord_node)

    def remove_random_node(self) -> None:
        node_id = random.choice(list(self.nodes.keys()))
        self.nodes.pop(node_id)
        print(f"Node {node_id} removed\n")

        self.message_sender.remove_node(node_id)

    def check_random_node(self) -> None:
        node_id: int = random.choice(list(self.nodes.keys()))
        print(f"Checking {node_id}:")
        target_id: int = random.randint(0, self.module - 1)

        self.message_sender.clear_message_counter()
        successor = self.message_sender.request_successor(self.nodes[node_id].get_node_info(), target_id)
        real_successor = self.message_sender.get_real_successor((target_id + 1) % self.module)

        messages_sent: int = self.message_sender.get_message_counter()
        self.max_messages_sent = max(self.max_messages_sent, messages_sent)
        self.total_messages_sent += messages_sent
        self.requests_count += 1

        # Just for fun
        self.nodes[node_id].stabilize()
        self.nodes[node_id].fix_finger()

        print(f"Searching for successor of id={target_id}...")
        print(f"It took {messages_sent} messages to find successor")
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
        print(f"Total requests made: {self.requests_count}")
        print(f"Maximum number of messages per request: {self.max_messages_sent}")
        print(f"Average number of messages per request: {self.total_messages_sent / self.requests_count}")

    def print_nodes(self) -> None:
        print(f"Chord ({len(self.nodes)} nodes):")
        for node_id in self.nodes:
            print(f"-- (ID = {node_id}): {self.nodes[node_id]}")
        print()
