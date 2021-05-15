import random
import threading
from typing import Optional, List, Tuple, Dict

from src import constants
from src.byte_message_type import ByteMessageType
from src.chat_message_type import ChatMessageType
from src.dht.chord_node import ChordNode
from src.dht.chord_node_request_sender import ChordNodeRequestSender
from src.dht.node_info import NodeInfo
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.message_redirection import MessageRedirection
from src.replication.info_key import InfoKey
from src.senders.long_polling_requests import LongPollingRequests
from src.senders.socket_message_sender import SocketMessageSender


class HashTable:
    def __init__(self, node_id: int,
                 message_sender: SocketMessageSender,
                 message_redirection: MessageRedirection) -> None:
        self.ip = message_sender.ip
        self.port = message_sender.port
        self.node_id = node_id

        self.long_polling = LongPollingRequests(message_sender, self.on_long_poll_failed)

        self.request_sender = ChordNodeRequestSender(self.long_polling)
        self.request_sender.set_message_sender(message_sender)

        message_redirection.subscribe(ByteMessageType.DHT_MESSAGE,
                                      self.request_sender.handle_request)

        self.node = ChordNode(constants.ID_LENGTH * 8, self.node_id, self.ip, self.port, self.request_sender)
        self.request_sender.set_current_node(self.node)

        self.possible_successor_interval: Tuple[int, int] = (10, 20)
        self.successor_list_interval: Tuple[int, int] = (30, 40)
        self.finger_interval: Tuple[int, int] = (30, 40)

        self.first_node_storing_value: Dict[int, NodeInfo] = {}
        self.node.replication_manager.set_first_node_changed_callback(self.on_first_node_moved)

    def subscribe(self, value_id: int, chat_message_type: ChatMessageType) -> None:
        first_node = self._find_node_storing_value(value_id)
        self.first_node_storing_value[value_id] = first_node

        request = self.long_polling.build_long_polling_request(value_id, chat_message_type)

        self.long_polling.add_long_polling_request(first_node.node_ip, first_node.node_port, request, value_id)

    def on_long_poll_failed(self, request: bytes) -> None:
        value_id, chat_message_type = self.long_polling.parse_long_polling_request(request)

        self.first_node_storing_value.pop(value_id)
        self.subscribe(value_id, chat_message_type)

    def on_first_node_moved(self, value_id: int) -> None:
        self.long_polling.cancel_long_polling_request(value_id)

    def join(self, invite_link: Optional[str]) -> None:
        if invite_link is None:
            self.node.join(None)
        else:
            other_id, other_ip, other_port = self._parse_invite_link(invite_link)
            self.node.join(NodeInfo(other_id, other_ip, other_port))

        self._run_stabilization()

    def get_invite_link(self) -> str:
        link = MessageBuilder.builder() \
            .append_id(self.node_id) \
            .append_bytes(self.ip) \
            .append_string(str(self.port)) \
            .build()
        return constants.base64_to_url(constants.bytes_to_string(link))

    @staticmethod
    def _parse_invite_link(invite_link: str) -> Tuple[int, bytes, int]:
        invite_link = constants.url_to_base64(invite_link)

        node_id: Container[int] = Container()
        ip: Container[bytes] = Container()
        port_string: Container[str] = Container()

        MessageParser.parser(constants.string_to_bytes(invite_link)) \
            .append_id(node_id) \
            .append_bytes(ip) \
            .append_string(port_string) \
            .parse()

        return node_id.get(), ip.get(), int(port_string.get())

    def get_single_value(self, value_type: ChatMessageType, value_id: int) -> Optional[bytes]:
        info_key = InfoKey(value_type, value_id)
        result = None
        while result is None:
            result = self.request_sender.get_value(self._find_node_storing_value(value_id),
                                                   info_key)
        return result

    def get_all_values(self, value_type: ChatMessageType, value_id: int) -> List[bytes]:
        info_key = InfoKey(value_type, value_id)
        result = None
        while result is None:
            result = self.request_sender.get_all_values(self._find_node_storing_value(value_id),
                                                        info_key)
        return result

    def set_value(self, value_type: ChatMessageType, value_id: int, value: bytes) -> None:
        info_key = InfoKey(value_type, value_id)
        while self.request_sender.set_value(self._find_node_storing_value(value_id),
                                            info_key, value) is None:
            continue

    def append_value(self, value_type: ChatMessageType, value_id: int, value: bytes) -> int:
        info_key = InfoKey(value_type, value_id)
        result = None
        while result is None:
            result = self.request_sender.append_value(self._find_node_storing_value(value_id),
                                                      info_key, value)
        return result

    def edit_value(self, value_type: ChatMessageType, value_id: int,
                   value_index: int, new_value: bytes) -> None:
        info_key = InfoKey(value_type, value_id)
        while self.request_sender.edit_value(self._find_node_storing_value(value_id),
                                             info_key, value_index, new_value) is None:
            continue

    def _find_node_storing_value(self, value_id: int) -> NodeInfo:
        if value_id in self.first_node_storing_value:
            return self.first_node_storing_value[value_id]
        return self.node.find_successor(value_id)

    def _run_stabilization(self) -> None:
        self._run_fix_possible_successors()
        self._run_fix_successor_list()
        self._run_fix_finger()

    def _fix_possible_successor(self) -> None:
        self.node.check_possible_successor()
        self._run_fix_possible_successors()

    def _run_fix_possible_successors(self) -> None:
        threading.Timer(random.randint(*self.possible_successor_interval), self._fix_possible_successor).start()

    def _fix_successor_list(self) -> None:
        self.node.update_successor_list()
        self._run_fix_successor_list()

    def _run_fix_successor_list(self) -> None:
        threading.Timer(random.randint(*self.successor_list_interval), self._fix_successor_list).start()

    def _fix_finger(self) -> None:
        self.node.fix_finger()
        self._run_fix_finger()

    def _run_fix_finger(self) -> None:
        threading.Timer(random.randint(*self.finger_interval), self._fix_finger).start()
