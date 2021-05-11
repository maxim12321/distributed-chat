import React, {useEffect} from "react";
import {connect} from "react-redux";

import {Messages as BaseMessages} from "../components";
import {messagesActions} from "../redux/actions";
import {ChatInput, Messages} from "./index";

const Dialogs = ({currentDialogId, lastMessage, fetchMessages, items}) => {
    console.log(currentDialogId)
    useEffect(() => {
        const interval = setInterval(() => {
            if (currentDialogId) {
                fetchMessages(currentDialogId);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, [currentDialogId]);

    return (
        <div className="chat__dialog">
            <div className="chat__dialog-header">
                <div className="chat__dialog-header-center">
                    <b className="chat__dialog-header-username"> {currentDialogId} </b>
                </div>
            </div>
            <div className="chat__dialog-messages">
                <BaseMessages items={items}/>
            </div>
            <div className="chat__dialog-input">
                <ChatInput/>
            </div>
        </div>
    );
}

export default connect(
    ({dialogs, messages}) => ({
        currentDialogId: dialogs.currentDialogId,
        items: messages.items
    }),
    messagesActions
)(Dialogs);