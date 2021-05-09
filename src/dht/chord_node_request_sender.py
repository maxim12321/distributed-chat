from enum import IntEnum
from typing import List, Optional, Callable, Dict, Tuple

from src import constants
from src.dht.chord_node import ChordNode
from src.dht.node_info import NodeInfo
from src.dht.node_request_sender import NodeRequestSender
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser
from src.replication.info_key import InfoKey
from src.replication.replication_data import ReplicationData
from src.replication.replication_info import ReplicationInfo
from src.senders.message_sender import MessageSender


class ChordRequestType(IntEnum):
    PING = 0,
    REQUEST_SUCCESSOR = 1,
    REQUEST_NEXT_NODE = 2,
    REQUEST_PREVIOUS_NODE = 3,
    REQUEST_PRECEDING_FINGER = 4,
    REQUEST_SUCCESSOR_LIST = 5,
    REQUEST_REPLICATION_INFO = 6,
    REQUEST_DATA_BY_KEYS = 7,
    PROPOSE_FINGER_UPDATE = 8,
    PROPOSE_PREDECESSOR = 9,
    UPDATE_REPLICATION_INFO = 10,
    UPDATE_REPLICATION = 11,
    GET_VALUE = 12,
    GET_ALL_VALUES = 13,
    SET_VALUE = 14,
    APPEND_VALUE = 15


class ChordNodeRequestSender(NodeRequestSender):
    def __init__(self) -> None:
        self.message_sender: Optional[MessageSender] = None

        self.node: Optional[ChordNode] = None
        self.node_id: Optional[int] = None

        self.answers: Dict[ChordRequestType, Callable[[bytes], bytes]] = {
            ChordRequestType.PING: self.ping_answer,
            ChordRequestType.REQUEST_SUCCESSOR: self.request_successor_answer,
            ChordRequestType.REQUEST_NEXT_NODE: self.request_next_node_answer,
            ChordRequestType.REQUEST_PREVIOUS_NODE: self.request_previous_node_answer,
            ChordRequestType.REQUEST_PRECEDING_FINGER: self.request_preceding_finger_answer,
            ChordRequestType.REQUEST_SUCCESSOR_LIST: self.request_successor_list_answer,
            ChordRequestType.REQUEST_REPLICATION_INFO: self.request_replication_info_answer,
            ChordRequestType.REQUEST_DATA_BY_KEYS: self.request_data_by_keys_answer,
            ChordRequestType.PROPOSE_FINGER_UPDATE: self.propose_finger_update_receive,
            ChordRequestType.PROPOSE_PREDECESSOR: self.propose_predecessor_receive,
            ChordRequestType.UPDATE_REPLICATION_INFO: self.update_replication_info_receive,
            ChordRequestType.UPDATE_REPLICATION: self.update_replication_receive,
            ChordRequestType.GET_VALUE: self.get_value_answer,
            ChordRequestType.GET_ALL_VALUES: self.get_all_values_answer,
            ChordRequestType.SET_VALUE: self.set_value_receive,
            ChordRequestType.APPEND_VALUE: self.append_value_receive,
        }

    def set_message_sender(self, message_sender: MessageSender) -> None:
        self.message_sender = message_sender

    def set_current_node(self, node: ChordNode) -> None:
        self.node = node
        self.node_id = node.node_info.node_id

    def handle_request(self, request: bytes) -> bytes:
        request_type: Container[ChordRequestType] = Container()

        data = MessageParser.parser(request) \
            .append_type(request_type) \
            .parse()

        return self.answers[request_type.get()](data)

    def ping(self, node: NodeInfo) -> bool:
        if node.node_id == self.node_id:
            return True

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.PING) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return False

        node_id: Container[int] = Container()
        MessageParser.parser(answer) \
            .append_id(node_id) \
            .parse()
        return node_id.get() == node.node_id

    def ping_answer(self, _: bytes) -> bytes:
        return MessageBuilder.builder() \
            .append_id(self.node_id) \
            .build()

    def request_successor(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        if node.node_id == self.node_id:
            return self.node.find_successor(target_id)

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_SUCCESSOR) \
            .append_id(target_id) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        node_info = NodeInfo()
        MessageParser.parser(answer) \
            .append_serializable(node_info) \
            .parse()
        return node_info

    def request_successor_answer(self, data: bytes) -> bytes:
        return self._answer_node_info_by_id(data, self.node.find_successor)

    def request_next_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        if node.node_id == self.node_id:
            return self.node.get_next_node()

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_NEXT_NODE) \
            .build()

        return self._make_node_info_request(node, request)

    def request_next_node_answer(self, _: bytes) -> bytes:
        answer: NodeInfo = self.node.get_next_node()

        return MessageBuilder.builder() \
            .append_serializable(answer) \
            .build()

    def request_previous_node(self, node: NodeInfo) -> Optional[NodeInfo]:
        if node.node_id == self.node_id:
            return self.node.get_previous_node()

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_PREVIOUS_NODE) \
            .build()

        return self._make_node_info_request(node, request)

    def request_previous_node_answer(self, _: bytes) -> bytes:
        answer: NodeInfo = self.node.get_previous_node()

        return MessageBuilder.builder() \
            .append_serializable(answer) \
            .build()

    def request_preceding_finger(self, node: NodeInfo, target_id: int) -> Optional[NodeInfo]:
        if node.node_id == self.node_id:
            return self.node.find_preceding_finger(target_id)

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_PRECEDING_FINGER) \
            .append_id(target_id) \
            .build()

        return self._make_node_info_request(node, request)

    def request_preceding_finger_answer(self, data: bytes) -> bytes:
        return self._answer_node_info_by_id(data, self.node.find_preceding_finger)

    def request_successor_list(self, node: NodeInfo) -> Optional[List[NodeInfo]]:
        if node.node_id == self.node_id:
            return self.node.get_successor_list()

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_SUCCESSOR_LIST) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        successors: Container[List[NodeInfo]] = Container()
        MessageParser.parser(answer) \
            .append_serializable_list(successors, NodeInfo) \
            .parse()

        return successors.get()

    def request_successor_list_answer(self, _: bytes) -> bytes:
        answer: List[NodeInfo] = self.node.get_successor_list()

        return MessageBuilder.builder() \
            .append_serializable_list(answer) \
            .build()

    def request_replication_info(self, node: NodeInfo) -> Optional[ReplicationInfo]:
        if node.node_id == self.node_id:
            return self.node.get_replication_info()

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_REPLICATION_INFO) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        replication_info = ReplicationInfo()
        MessageParser.parser(answer) \
            .append_serializable(replication_info) \
            .parse()
        return replication_info

    def request_replication_info_answer(self, _: bytes) -> bytes:
        answer: ReplicationInfo = self.node.get_replication_info()

        return MessageBuilder.builder() \
            .append_serializable(answer) \
            .build()

    def request_data_by_keys(self, node: NodeInfo, info_keys: List[InfoKey]) -> Optional[ReplicationData]:
        if node.node_id == self.node_id:
            return self.node.get_data_by_keys(info_keys)

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.REQUEST_DATA_BY_KEYS) \
            .append_object(list(map(str, info_keys))) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        replication_data = ReplicationData()
        MessageParser.parser(answer) \
            .append_serializable(replication_data) \
            .parse()
        return replication_data

    def request_data_by_keys_answer(self, data: bytes) -> bytes:
        keys: Container[List[str]] = Container()
        MessageParser.parser(data) \
            .append_object(keys) \
            .parse()

        info_keys: List[InfoKey] = list(map(InfoKey.from_string, keys.get()))

        answer: ReplicationData = self.node.get_data_by_keys(info_keys)

        return MessageBuilder.builder() \
            .append_serializable(answer) \
            .build()

    def propose_finger_update(self, node: NodeInfo, node_to_update: NodeInfo, finger_number: int) -> Optional[bytes]:
        if node.node_id == self.node_id:
            self.node.propose_finger_update(node_to_update, finger_number)
            return b''

        message = MessageBuilder.builder() \
            .append_type(ChordRequestType.PROPOSE_FINGER_UPDATE) \
            .append_serializable(node_to_update) \
            .append_object(finger_number) \
            .build()

        return self.message_sender.send_request(node.node_ip, node.node_port, message)

    def propose_finger_update_receive(self, data: bytes) -> bytes:
        node_to_update: NodeInfo = NodeInfo()
        finger_number: Container[int] = Container()

        MessageParser.parser(data) \
            .append_serializable(node_to_update) \
            .append_object(finger_number) \
            .parse()

        self.node.propose_finger_update(node_to_update, finger_number.get())
        return b''

    def propose_predecessor(self, node: NodeInfo, node_to_propose: NodeInfo) -> Optional[bytes]:
        if node.node_id == self.node_id:
            self.node.update_previous_node(node_to_propose)
            return b''

        message = MessageBuilder.builder() \
            .append_type(ChordRequestType.PROPOSE_PREDECESSOR) \
            .append_serializable(node_to_propose) \
            .build()

        return self.message_sender.send_request(node.node_ip, node.node_port, message)

    def propose_predecessor_receive(self, data: bytes) -> bytes:
        node_to_propose: NodeInfo = NodeInfo()

        MessageParser.parser(data) \
            .append_serializable(node_to_propose) \
            .parse()

        self.node.update_previous_node(node_to_propose)
        return b''

    def update_replication_info(self, node: NodeInfo, new_info: ReplicationInfo) -> Optional[bytes]:
        if node.node_id == self.node_id:
            self.node.update_replication_info(new_info)
            return b''

        message = MessageBuilder.builder() \
            .append_type(ChordRequestType.UPDATE_REPLICATION_INFO) \
            .append_serializable(new_info) \
            .build()

        return self.message_sender.send_request(node.node_ip, node.node_port, message)

    def update_replication_info_receive(self, data: bytes) -> bytes:
        new_info: ReplicationInfo = ReplicationInfo()

        MessageParser.parser(data) \
            .append_serializable(new_info) \
            .parse()

        self.node.update_replication_info(new_info)
        return b''

    def update_replication(self, node: NodeInfo,
                           new_info: ReplicationInfo, new_data: ReplicationData) -> Optional[bytes]:
        if node.node_id == self.node_id:
            self.node.update_replication(new_info, new_data)
            return b''

        message = MessageBuilder.builder() \
            .append_type(ChordRequestType.UPDATE_REPLICATION) \
            .append_serializable(new_info) \
            .append_serializable(new_data) \
            .build()

        return self.message_sender.send_request(node.node_ip, node.node_port, message)

    def update_replication_receive(self, data: bytes) -> bytes:
        new_info: ReplicationInfo = ReplicationInfo()
        new_data: ReplicationData = ReplicationData()

        MessageParser.parser(data) \
            .append_serializable(new_info) \
            .append_serializable(new_data) \
            .parse()

        self.node.update_replication(new_info, new_data)
        return b''

    def get_value(self, node: NodeInfo, key: InfoKey) -> Optional[bytes]:
        if node.node_id == self.node_id:
            return self.node.get_value(key)

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.GET_VALUE) \
            .append_string(str(key)) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        value: Container[bytes] = Container()
        MessageParser.parser(answer) \
            .append_optional_bytes(value) \
            .parse()
        return value.get()

    def get_value_answer(self, data: bytes) -> bytes:
        key_string: Container[str] = Container()
        MessageParser.parser(data) \
            .append_string(key_string) \
            .parse()

        info_key = InfoKey.from_string(key_string.get())

        answer: Optional[bytes] = self.node.get_value(info_key)

        return MessageBuilder.builder() \
            .append_optional_bytes(answer) \
            .build()

    def get_all_values(self, node: NodeInfo, key: InfoKey) -> Optional[List[bytes]]:
        if node.node_id == self.node_id:
            return self.node.get_all_values(key)

        request = MessageBuilder.builder() \
            .append_type(ChordRequestType.GET_ALL_VALUES) \
            .append_string(str(key)) \
            .build()

        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        values: Container[List[bytes]] = Container()
        MessageParser.parser(answer) \
            .append_object(values) \
            .parse()
        return values.get()

    def get_all_values_answer(self, data: bytes) -> bytes:
        key_string: Container[str] = Container()
        MessageParser.parser(data) \
            .append_string(key_string) \
            .parse()

        info_key = InfoKey.from_string(key_string.get())

        answer: Optional[List[bytes]] = self.node.get_all_values(info_key)
        if answer is None:
            answer = []
        answer: List[dict] = [constants.bytes_to_dict(value) for value in answer]

        return MessageBuilder.builder() \
            .append_object(answer) \
            .build()

    def set_value(self, node: NodeInfo, key: InfoKey, value: bytes) -> Optional[bytes]:
        if node.node_id == self.node_id:
            self.node.set_value(key, value)
            return b''

        return self._make_info_key_value_request(node, key, value, ChordRequestType.SET_VALUE)

    def set_value_receive(self, data: bytes) -> bytes:
        info_key, value = self._receive_info_key_value(data)

        self.node.set_value(info_key, value)
        return b''

    def append_value(self, node: NodeInfo, key: InfoKey, value: bytes) -> Optional[bytes]:
        if node.node_id == self.node_id:
            self.node.append_value(key, value)
            return b''

        return self._make_info_key_value_request(node, key, value, ChordRequestType.APPEND_VALUE)

    def append_value_receive(self, data: bytes) -> bytes:
        info_key, value = self._receive_info_key_value(data)

        self.node.append_value(info_key, value)
        return b''

    def _make_node_info_request(self, node: NodeInfo, request: bytes) -> Optional[NodeInfo]:
        answer: Optional[bytes] = self.message_sender.send_request(node.node_ip, node.node_port, request)
        if answer is None:
            return None

        node_info = NodeInfo()
        MessageParser.parser(answer) \
            .append_serializable(node_info) \
            .parse()
        return node_info

    def _make_info_key_value_request(self, node: NodeInfo, key: InfoKey, value: bytes,
                                     request_type: ChordRequestType) -> Optional[bytes]:
        message = MessageBuilder.builder() \
            .append_type(request_type) \
            .append_string(str(key)) \
            .append_bytes(value) \
            .build()

        return self.message_sender.send_request(node.node_ip, node.node_port, message)

    @staticmethod
    def _receive_info_key_value(data: bytes) -> Tuple[InfoKey, bytes]:
        key_string: Container[str] = Container()
        value: Container[bytes] = Container()

        MessageParser.parser(data) \
            .append_string(key_string) \
            .append_bytes(value) \
            .parse()

        return InfoKey.from_string(key_string.get()), value.get()

    @staticmethod
    def _answer_node_info_by_id(data: bytes, id_to_node_info: Callable[[int], NodeInfo]) -> bytes:
        target_id: Container[int] = Container()

        MessageParser.parser(data) \
            .append_id(target_id) \
            .parse()

        answer: NodeInfo = id_to_node_info(target_id.get())

        return MessageBuilder.builder() \
            .append_serializable(answer) \
            .build()
