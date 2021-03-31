from typing import List


class User:
    def __init__(self):
        self.network_time = 0
        # this must be loaded from file
        self.usernames = {}
        self.ip = {}
        self.chat_id_lists = {}
        self.messages_lists = {}
        self.user_id_lists_from_current_chat = {}

    def update_ip(self, user_id: int, ip: bytes) -> None:
        self.ip[user_id] = ip

    def get_ip(self, user_id: int) -> bytes:
        return self.ip[user_id]

    def get_user_by_username(self, username: bytes) -> int:
        return self.usernames[username]

    def add_user_to_chat(self, user_id: int, chat_id: int) -> None:
        self.chat_id_lists[user_id].append(chat_id)
        self.user_id_lists_from_current_chat[chat_id].append(user_id)

    def get_chat_user_list(self, chat_id: int) -> List[int]:
        return self.user_id_lists_from_current_chat[chat_id]

    def get_user_chat_list(self, chat_id: int) -> List[int]:
        return self.user_id_lists_from_current_chat[chat_id]

    def get_message_list(self, chat_id: int) -> List[bytes]:
        return self.messages_lists[chat_id]

    def new_message(self, chat_id: int, message: bytes) -> None:
        self.messages_lists[chat_id].append(message)
