from text_message import TextMessage
import constants


class MessageHandler:
    def __init__(self):
        self.user_id_list = []
        self.message_list = []

    def handle_text_message(self, message: bytes) -> None:
        sender_id = message[:constants.ID_LENGTH]
        text_message = message[constants.ID_LENGTH:]
        self.message_list.append(TextMessage(sender_id, text_message))

    def handle_introduce_user(self, id: bytes) -> None:
        self.user_id_list.append(id)

    def handle_user_list(self, message: bytes) -> None:
        self.user_id_list.clear()
        for current_byte in range(0, len(message), constants.ID_LENGTH):
            self.user_id_list.append(message[current_byte:current_byte + constants.ID_LENGTH])

    def get_user_id_list(self):
        return self.user_id_list
