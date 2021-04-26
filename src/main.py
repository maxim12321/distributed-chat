from user import User

if __name__ == "__main__":
    user = User()
    while True:
        fin = input("Type command: ")
        if fin == "1":
            name = input("You wanted to create chat. Please write name of this chat: ")
            user.create_chat(name)
            print("You created chat with the name:", name)
        if fin == "2":
            temp = user.get_chat_list()
            print("Your chat list is:")
            for chat in temp:
                print(chat, temp[chat].chat_name)

        if fin == "3":
            chat_id = input("Write chat_id to create link: ")
            link = user.get_invite_link(int(chat_id))
            print("Copy this link to add users in this chat:")
            print(link)

        if fin == "4":
            link = input("Insert link to join chat: ")
            user.join_chat_by_link(link)
            print("Done. Check your chats now")
