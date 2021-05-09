import React from "react";

import "./DialogItem.scss";
import { Avatar } from "../"

const DialogItem = ({ user, message }) => (
  <div className="border">
    <div className="dialogs__item">
      <div className="dialogs__item-avatar">
        <Avatar user={user}/>
      </div>
      <div className="dialogs__item-info">
        <div className="dialogs__item-info-top">
          <b>{user.fullname}</b>
          <span>
            {message.created}
          </span>
        </div>
        <div className="dialogs__item-info-bottom">
          <p>{message.text}</p>
        </div>
      </div>
    </div>
  </div>
);

export default DialogItem;