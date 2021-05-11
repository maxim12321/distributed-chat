from src.chat import Chat
from src.user import User


def print_chat(chat: Chat) -> None:
    print(f"Chat '{user.get_chat_info(chat_id).chat_name}' (id={chat.chat_id}):")
    print("\tUsers:")
    for user_info in chat.get_user_id_list():
        print(f"\t\t{user_info.user_id}")
    print("\tMessages:")
    for message in chat.get_message_list():
        print(f"\t\t{message.sender_id}, {message.context}")


if __name__ == "__main__":
    username = input("Input your username: ")
    user = User(username)
    print(f"Welcome, {username}")
    print(f"You can invite users with link: {user.get_network_invite_link()}\n")

    while True:
        print("=========================")
        print("0 -- Join by invite link")
        print("1 -- Create chat")
        print("2 -- Print chat_list")
        print("3 -- Get invite_link")
        print("4 -- Join by invite_link")
        print("5 -- Send message")
        print("=========================")
        fin = input("Type command: ")

        if fin == "0":
            network_invite_link = input("Write network_invite_link (or -1): ")
            user.join_network_by_invite_link(None if network_invite_link == "-1" else network_invite_link)

        if fin == "1":
            name = input("You wanted to create chat. Please write name of this chat: ")
            user.create_chat(name)
            print("You created chat with the name:", name)

        if fin == "2":
            chat_id_list = user.get_chat_id_list()
            print("Your chat list is:")
            for chat_id in chat_id_list:
                print_chat(user.get_chat_info(chat_id))

        if fin == "3":
            chat_id = input("Write chat_id to create link: ")
            link = user.get_invite_link(int(chat_id))
            print("Copy this link to add users in this chat:")
            print(link)

        if fin == "4":
            link = input("Insert link to join chat: ")
            user.join_chat_by_link(link)
            print("Done. Check your chats now")

        if fin == "5":
            chat_id = input("Write chat_id: ")
            text = input("Write text: ")
            user.send_text_message(int(chat_id), text)

        if fin == "debug":
            print(f"My id: {user.user_id}")
            print(f"Successor id: {user.hash_table.node.successor.node_id}")
            print(f"Predecessor id: {user.hash_table.node.predecessor.node_id}")
            print(f"Replication info:\n{user.hash_table.node.get_replication_info()}\n")
            print(f"Replication data:\n{user.hash_table.node.replication_manager.data}\n")
