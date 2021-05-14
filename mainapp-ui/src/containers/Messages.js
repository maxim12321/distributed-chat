import React, {useEffect, useState} from "react";
import {connect} from "react-redux";

import {Messages as BaseMessages} from "../components";
import {messagesActions} from "../redux/actions";
import {ChatInput} from "./index";

const Dialogs = ({currentDialogId, fetchMessages, getChatNameById, getInviteLinkById, items}) => {
    const [chatName, setChatName] = useState("");
    const [inviteLink, setInviteLink] = useState("");

    console.log(currentDialogId)
    useEffect(() => {
        const interval = setInterval(() => {
            if (currentDialogId) {
                fetchMessages(currentDialogId);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, [currentDialogId]);

    const getChatName = () => {
        if (currentDialogId == null) {
            return "Choose dialog";
        }

        getChatNameById(currentDialogId).then(response => setChatName(response.data))
        return chatName;
    }

    const getInviteLink = () => {
        if (currentDialogId == null) {
            return "";
        }

        getInviteLinkById(currentDialogId).then(response => setInviteLink(response.data))
        return (<a href={inviteLink}>Invite link</a>)
    }

    return (
        <div className="chat__dialog">
            <div className="chat__dialog-header">
                <div className="chat__dialog-header-center">
                    <b className="chat__dialog-header-username"> {getChatName()} </b>
                    {getInviteLink()}
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
