import React, { useState } from "react";
import PropTypes from "prop-types";
import add_image from '../../resources/add_image.png';
import send_message from '../../resources/send_message.png';
import { UploadField } from '@navjobs/upload'

import "./ChatInput.scss";
import { Button } from "../";

const ChatInput = props => {
  const [value, setValue] = useState("");
  const  { onSendMessage, currentDialogId } = props;

  const handleSendMessage = (e) => {
    if (e.keyCode === 13) {
      setValue('');
      if (value.trim() !== "") {
        onSendMessage(value, currentDialogId);
      }
    }
  };

  return (
  <div className="chat-input">
    <input
      className="chat-input-send"
      type="text"
      placeholder="Введите текст"
      onKeyUp={handleSendMessage}
      onChange={e => setValue(e.target.value)}
      value={value}
    />
    <div className="chat-input__actions">
      <UploadField
        onFiles={files => console.log(files)}
        containerProps={{
          className: "input__actions-upload"
        }}
        uploadProps={{
          accept: ".jpg,.png,.jpeg,.gif,.svg,.bmp",
          multiple: "multiple"
        }}
      >
      <img className="chat-input__actions-add" src={add_image} alt = "add_image"/>
      </UploadField>
      <img className="chat-input__actions-send" src={send_message} alt = "send_message"/>
    </div>
  </div>
  )
};

ChatInput.propTypes = {
  className: PropTypes.string
};

export default ChatInput;