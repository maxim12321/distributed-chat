import {axios} from "../../core";

export default {
    sendChatName: chatName => {
        axios.post("/create_chat", {
            chat_name: chatName
        });
    }
};
