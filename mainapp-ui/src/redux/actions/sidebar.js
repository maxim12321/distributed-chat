import {sidebarApi} from "../../utils/api";

const actions = {
    sendChatName: chatName => dispatch => {
        sidebarApi.sendChatName(chatName)
    },
    getNetworkInviteLink: () => dispatch => sidebarApi.getNetworkInviteLink()
};

export default actions;
