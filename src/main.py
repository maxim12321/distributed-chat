from src.user import User

if __name__ == "__main__":
    username = input("Input your username: ")
    user = User(username)
    print(f"Welcome, {username}")
    while True:
        print("=========================")
        print("1 -- Create chat")
        print("2 -- Print chat_list")
        print("3 -- Get invite_link")
        print("4 -- Join by invite_link")
        print("5 -- Send message")
        print("=========================")
        fin = input("Type command: ")
        if fin == "1":
            name = input("You wanted to create chat. Please write name of this chat: ")
            user.create_chat(name)
            print("You created chat with the name:", name)
        if fin == "2":
            chat_id_list = user.get_chat_id_list()
            print("Your chat list is:")
            for chat_id in chat_id_list:
                print(chat_id, user.get_chat_info(chat_id).chat_name)
                eeeee = user.get_chat_info(chat_id).get_message_list()
                for message in eeeee:
                    print(f"     {message.sender_id}, {message.context}")

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