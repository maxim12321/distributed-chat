import React from "react";
import {connect} from "react-redux";

import {ChatInput as ChatInputBase} from "../components";
import {messagesActions} from "../redux/actions";

const ChatInput = ({sendMessage, sendImages, currentDialogId}) => {
    return (
        <ChatInputBase
            onSendMessage={sendMessage}
            onSendImages={sendImages}
            currentDialogId={currentDialogId}
        />
    );
}

export default connect(
    ({dialogs}) => dialogs,
    messagesActions
)(ChatInput);
