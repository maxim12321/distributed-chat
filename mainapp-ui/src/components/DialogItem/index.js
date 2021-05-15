import React from "react";

import "./DialogItem.scss";
import {Avatar} from "../"

const DialogItem = ({_id, user, message, onSelect}) => {
    return (
        <div className="border">
            <div className="dialogs__item" onClick={onSelect.bind(this, _id)}>
                <div className="dialogs__item-avatar">
                    <Avatar user={user}/>
                </div>
                <div className="dialogs__item-info">
                    <div className="dialogs__item-info-top">
                        <b>{user.fullname}</b>
                        <span>{message.created}</span>
                    </div>
                    <div className="dialogs__item-info-bottom">
                        <p>{message.text}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default DialogItem;
