from typing import Any, Generator, Optional

from src import constants
from src.serializable import Serializable


class NodeInfo(Serializable):
    def __init__(self, node_id: Optional[int] = None,
                 node_ip: Optional[bytes] = None,
                 node_port: Optional[int] = None) -> None:
        self.node_id: Optional[int] = node_id
        self.node_ip: Optional[bytes] = node_ip
        self.node_port: Optional[int] = node_port

    def __iter__(self) -> Generator[str, Any, None]:
        yield from {
            "node_id": self.node_id,
            "node_ip": constants.bytes_to_dict(self.node_ip),
            "node_port": self.node_port
        }.items()

    def load_from_dict(self, data: dict) -> None:
        self.node_id = data["node_id"]
        self.node_ip = data["node_ip"]
        self.node_port = data["node_port"]
