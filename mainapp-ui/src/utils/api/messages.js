import {axios} from "../../core";

export default {
    getAllByDialogId: id => axios.get("/messages?dialog=" + id),
    send: (text, currentDialogId) => {
        axios.post("/send", {
            text: text,
            chat_id: currentDialogId
        });
    },
    sendUserName: userName => {
        axios.post("/set_username", {
            user_name: userName
        }).then(() => {
            window.location.href = axios.defaults.baseURL;
        });
    },
    getChatNameById: chatId => axios.get("/get_chat_name?chat_id=" + chatId),
    getInviteLinkById: chatId => axios.get("/get_invite_link?chat_id=" + chatId)
};
