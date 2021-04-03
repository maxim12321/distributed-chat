from dataclasses import dataclass


@dataclass
class TextMessage:
    sender_id: bytes
    context: bytes
