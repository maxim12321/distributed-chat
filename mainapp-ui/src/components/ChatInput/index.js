import React, {useState} from "react";
import PropTypes from "prop-types";
import add_image from '../../resources/add_image.png';
import send_message from '../../resources/send_message.png';
import {UploadField} from '@navjobs/upload'

import "./ChatInput.scss";

const ChatInput = props => {
    const [value, setValue] = useState("");
    const {onSendMessage, onSendImages, currentDialogId} = props;

    const handleSendMessage = (e) => {
        if (e.keyCode === 13) {
            setValue('');
            if (value.trim() !== "") {
                onSendMessage(value, currentDialogId);
            }
        }
    };

    const handleSelectedFiles = (files) => {
        if (files.length === 0) {
            return;
        }
        onSendImages(files, currentDialogId);
    }

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
                    onFiles={handleSelectedFiles}
                    containerProps={{
                        className: "input__actions-upload"
                    }}
                    uploadProps={{
                        accept: ".jpg,.png,.jpeg,.gif,.svg,.bmp",
                        multiple: "multiple"
                    }}
                >
                    <img className="chat-input__actions-add" src={add_image} alt="add_image"/>
                </UploadField>
                <img className="chat-input__actions-send" src={send_message} alt="send_message"/>
            </div>
        </div>
    )
};

ChatInput.propTypes = {
    className: PropTypes.string
};

export default ChatInput;
