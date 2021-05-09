import React from "react";
import PropTypes from "prop-types";
import add_image from '../../resources/add_image.png';
import send_message from '../../resources/send_message.png';

import "./ChatInput.scss";

const ChatInput = props => (
  <div className="chat-input">
    <input className="chat-input-send" type="text" placeholder="Введите текст"/>
    <div className="chat-input__actions">
      <img className="chat-input__actions-add" src={add_image} />
      <img className="chat-input__actions-send" src={send_message} />
    </div>
  </div>
);

ChatInput.propTypes = {
  className: PropTypes.string
};

export default ChatInput;