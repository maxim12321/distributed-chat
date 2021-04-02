class TextMessage:
    def __init__(self, sender_id: bytes, message: bytes):
        self.sender_id = sender_id
        self.message = message
