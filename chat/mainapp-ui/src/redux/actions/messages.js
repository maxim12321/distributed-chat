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
    }
};

export default actions;