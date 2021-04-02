from text_message import TextMessage


class MessageHandler:
    def __init__(self):
        self.ID_LENGTH = 16

    def handle_text_message(self, message: bytes, message_list: list) -> None:
        sender_id = message[:self.ID_LENGTH]
        text_message = message[self.ID_LENGTH:]
        message_list.append(TextMessage(sender_id, text_message))

    def handle_introduce_user(self, id: bytes, user_id_list: list) -> None:
        user_id_list.append(id)

    def handle_user_list(self, message: bytes, user_id_list: list) -> None:
        user_id_list.clear()
        for current_byte in range(0, len(message), self.ID_LENGTH):
            user_id_list.append(message[current_byte:current_byte + self.ID_LENGTH])
