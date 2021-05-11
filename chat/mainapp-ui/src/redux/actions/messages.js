import { messagesApi } from "../../utils/api";

const actions = {
  setMessages: items => ({
    type: "MESSAGES:SET_ITEMS",
    payload: items
  }),
  fetchSendMessage: text => dispatch => {
    messagesApi.send(text);
  },
  fetchMessages : dialogId => dispatch => {
    messagesApi
      .getAllByDialogId(dialogId)
      .then(({ data }) => {
        dispatch(actions.setMessages(data));
      });
  }
};

export default actions;