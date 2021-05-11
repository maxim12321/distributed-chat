import React from "react";
import PropTypes from "prop-types";
import dialog_empty from '../../resources/dialog_empty.png';

import "./Messages.scss";
import { Message } from "../"

const Messages = ({ items })  => (

  <div className="messages">
     {(items) ? (
       <div>
         {items.map(item => (
           <Message {...item} />
         ))}
       </div>
     ) : (
      <div className="messages-empty">
        <img className="messages-empty-image" src={dialog_empty} alt="dialog_empty"/>
        <p>Диалог пуст или не открыт</p>
      </div>
    )}
  </div>
);


Messages.propTypes = {
  items: PropTypes.array
};

export default Messages;