from user import User


def print_user_info(user):
    print(f'Info about {user.get_username()}')
    print(f"  It's ip: {user.get_ip()}")
    print(f"  It's id: {user.get_id()}")
    print('  --')
    print("  User chat list is:")
    chat_id_list = user.get_chat_id_list()
    for chat_id in chat_id_list:
        chat = user.get_chat_info(chat_id)
        print('    ---')
        print(f"    ChatId: {chat.get_chat_id()}, ChatName: {chat.get_chat_name()}")
        print(f"      User list in this chat:")
        for flex in chat.get_user_id_list():
            print(f'        {flex.user_id}, {flex.ip}')
        print("      --")
        print('      Messages:')
        for flex in chat.get_message_list():
            print(f'        {flex.sender_id}, {flex.context}')

    print('========================')
    print('========================')


if __name__ == "__main__":
    user1 = User("Squirell")
    user2 = User("Rabbit")

    user1.create_chat("Test Chat")
    print_user_info(user1)

    temp = user1.get_chat_id_list()
    id = temp[0]
    link = user1.get_invite_link(id)

    print('!!!!!!')
    print(link)
    print('!!!!!!')

    user2.join_chat_by_link(link)
    user1.send_text_message(temp[0], "Hola hola")

    print_user_info(user2)
    print_user_info(user1)

    print("ADDING NEW USER")

    user3 = User("Fluffy")
    print_user_info(user3)
    user3.create_chat("Fluffy_CHAT")
    print_user_info(user3)
    temp = user3.get_chat_id_list()
    id = temp[0]
    link = user3.get_invite_link(id)
    user3.send_text_message(id, 'Test мессаге')

    print('!!!!!!')
    print(link)
    print('!!!!!!')

    user1.join_chat_by_link(link)
    user2.join_chat_by_link(link)

    print_user_info(user1)
    print_user_info(user2)
    print_user_info(user3)

    # user = User()
    # while True:
    #     fin = input("Type command: ")
    #     if fin == "1":
    #         name = input("You wanted to create chat. Please write name of this chat: ")
    #         user.create_chat(name)
    #         print("You created chat with the name:", name)
    #     if fin == "2":
    #         temp = user.get_chat_list()
    #         print("Your chat list is:")
    #         for chat in temp:
    #             print(chat, temp[chat].chat_name)
    #
    #     if fin == "3":
    #         chat_id = input("Write chat_id to create link: ")
    #         link = user.get_invite_link(int(chat_id))
    #         print("Copy this link to add users in this chat:")
    #         print(link)
    #
    #     if fin == "4":
    #         link = input("Insert link to join chat: ")
    #         user.join_chat_by_link(link)
    #         print("Done. Check your chats now")
