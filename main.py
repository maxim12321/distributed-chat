import random
import socket

from src.dht.chord_node import ChordNode
from src.dht.chord_node_request_sender import ChordNodeRequestSender
from src.dht.node_info import NodeInfo
from src.replication.info_key import InfoKey
from src.senders.socket_message_sender import SocketMessageSender

if __name__ == "__main__":
    id_bit_length = 10
    module = 2 ** id_bit_length

    node_id = random.randrange(0, module)
    print(f"Welcome! Your id is {node_id}\n")

    print(f"Please, enter port: ", end="")
    ip = socket.inet_pton(socket.AF_INET, "127.0.0.1")
    port = int(input())

    request_sender = ChordNodeRequestSender()
    message_sender = SocketMessageSender(ip, port,
                                         None,
                                         request_sender.handle_request,
                                         None)
    request_sender.set_message_sender(message_sender)

    node = ChordNode(id_bit_length, node_id, ip, port, request_sender)
    request_sender.set_current_node(node)

    print("Enter some other node's id (or -1 if you're first): ", end="")
    other_id = int(input())

    if other_id == -1:
        node.join(None)
    else:
        print("And we need one more thing. Please, enter that node's port: ", end="")
        other_port = int(input())
        node.join(NodeInfo(other_id, ip, other_port))

    print("\nYou've joined successfully!\n")

    while True:
        print("Enter command (send, check): ", end="")
        command = input()

        if command == "send":
            print(f"Enter key for message (from 0 to {module - 1}): ", end="")
            key = int(input())

            print("Enter message you want to send: ", end="")
            message_bytes = input().encode("utf-8")

            node.append_value_by_key(InfoKey(1, key), message_bytes)

            print("Message was sent!\n")
        elif command == "check":
            print(f"Enter key for messages (from 0 to {module - 1}): ", end="")
            key = int(input())

            values = node.get_all_data_by_key(InfoKey(1, key))
            print("\nMessages:")
            if values is None:
                print("Empty :(")
            else:
                for value in values:
                    print(value.decode("utf-8"))
            print()
        elif command == "debug":
            print(f"My id: {node_id}")
            print(f"Successor id: {node.successor.node_id}")
            print(f"Predecessor id: {node.predecessor.node_id}")
            print(f"Replication info:\n{node.get_replication_info()}\n")
