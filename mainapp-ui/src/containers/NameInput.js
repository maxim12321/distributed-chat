import React from "react";
import {connect} from "react-redux";

import {NameInput as NameInputBase} from "../components";
import {messagesActions} from "../redux/actions";

const NameInput = ({sendUserName}) => {
    return (
        <NameInputBase
            onSendMessage={sendUserName}
        />
    );
}

export default connect(
    ({dialogs}) => dialogs,
    messagesActions
)(NameInput);
