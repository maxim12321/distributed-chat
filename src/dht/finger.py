from dataclasses import dataclass
from src.dht.node_info import NodeInfo


@dataclass
class Finger:
    # [start; end)
    start: int
    end: int
    node: NodeInfo
