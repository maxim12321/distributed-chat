import {messagesApi} from "../../utils/api";

const actions = {
    setMessages: items => ({
        type: "MESSAGES:SET_ITEMS",
        payload: items
    }),
    fetchSendMessage: (text, currentDialogId) => dispatch => {
        messagesApi.send(text, currentDialogId);
    },
    fetchMessages: dialogId => dispatch => {
        messagesApi
            .getAllByDialogId(dialogId)
            .then(({data}) => {
                dispatch(actions.setMessages(data));
            });
    },
    sendUserName: userName => dispatch => {
        messagesApi.sendUserName(userName);
    },
    getChatNameById: chatId => dispatch => messagesApi.getChatNameById(chatId),
    getInviteLinkById: chatId => dispatch => messagesApi.getInviteLinkById(chatId)
};

export default actions;
