import React from "react";
import {connect} from "react-redux";

import {Sidebar} from "../components";
import {sidebarActions} from "../redux/actions";

const SidebarContainer = ({getNetworkInviteLink, sendChatName}) => (
    <Sidebar getNetworkInviteLink={getNetworkInviteLink} sendChatName={sendChatName}/>
);

export default connect(
    ({user}) => ({user}),
    sidebarActions
)(SidebarContainer);
