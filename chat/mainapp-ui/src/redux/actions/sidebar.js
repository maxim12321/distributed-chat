import {sidebarApi} from "../../utils/api";

const actions = {
    sendChatName: chatName => dispatch => {
        sidebarApi.sendChatName(chatName)
    }
};

export default actions;