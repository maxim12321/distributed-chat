import {axios} from "../../core";

export default {
    getAllByDialogId: id => axios.get("/messages?dialog=" + id),
    send: (text, currentDialogId) => {
        axios.post("/send", {
            text: text,
            chat_id: currentDialogId
        });
    }
};
