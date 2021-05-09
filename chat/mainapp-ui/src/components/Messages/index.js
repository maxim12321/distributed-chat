import React from "react";
import dialog_empty from '../../resources/dialog_empty.png';

import "./Messages.scss";
import { Message } from "../"

const Messages = ({ items })  => (
  <div className="messages">
     {(items) ? (
       <Message
         avatar="https://yt3.ggpht.com/ytc/AAUvwniaWDANcEMK_t1tlbVca84Dn8J-sTY4G3eCBobo=s900-c-k-c0x00ffffff-no-rj"
         text="Антонио"
         date="22:03:29"
         isMe={true}
       />
     ) : (
      <div className="messages-empty">
        <img className="messages-empty-image" src={dialog_empty}/>
        <p>Диалог пуст или не открыт</p>
      </div>
    )}
  </div>
);

export default Messages;