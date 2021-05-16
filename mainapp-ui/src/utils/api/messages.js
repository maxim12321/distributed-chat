import {axios} from "../../core";

export default {
    getAllByDialogId: id => axios.get("/messages?dialog=" + id),
    send: (text, currentDialogId) => {
        axios.post("/send", {
            text: text,
            chat_id: currentDialogId
        });
    },
    sendImages: (images, currentDialogId) => {
        let readers = []

        for (const image of images) {
            readers.push(new Promise((resolve, reject) => {
                let reader = new FileReader();

                reader.onload = () => {
                    resolve(reader.result);
                };
                reader.onerror = () => {
                    reject(reader);
                };
                reader.readAsDataURL(image)
            }));
        }

        Promise.all(readers).then((imageUrls) => {
            axios.post("/send_images", {
                image_urls: imageUrls,
                chat_id: currentDialogId
            })
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
