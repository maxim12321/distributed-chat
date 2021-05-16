import React, {useState} from "react";
import PropTypes from "prop-types";
import classNames from "classnames";

import "./Message.scss";
import {Avatar} from "../"

const Message = ({avatar, user, text, date, isMe, attachments}) => {
    const [visible, setVisible] = useState(false);
    const [value, setValue] = useState("");

    const handleShowDialog = (imageUrl) => {
        setValue(imageUrl);
        setVisible(!visible);
    };

    return (
        <div className={classNames('message', {
            'message--isme': isMe,
            'message--image': attachments && attachments.length === 1
        })}
        >
            <div className="message__content">
                <div className="message__avatar">
                    <Avatar user={user}/>
                </div>
                <div className="message__info">
                    {text &&
                    <div className="message__bubble">
                        <p className="message__text">{text}</p>
                    </div>}
                    <div className="message__attachments">
                        {attachments &&
                        attachments.map(item => (
                            <div className="message__attachments-item">
                                <img
                                    className="message__attachments-item-small"
                                    src={item.url}
                                    alt={item.filename}
                                    onClick={() => {
                                        handleShowDialog(item.url)
                                    }}
                                />
                                {visible && (
                                    <dialog
                                        className="message__attachments-item-dialog"
                                        open
                                        onClick={() => {
                                            handleShowDialog(item.url)
                                        }}
                                    >
                                        <img
                                            className="image"
                                            src={value}
                                            alt={item.filename}
                                            onClick={() => {
                                                handleShowDialog(item.url)
                                            }}
                                        />
                                    </dialog>
                                )}
                            </div>
                        ))}
                    </div>
                    <span className="message__date">
          {date}
        </span>
                </div>
            </div>
        </div>
    );
}

Message.defaultProps = {
    user: {}
};

Message.propTypes = {
    avatar: PropTypes.string,
    text: PropTypes.string,
    date: PropTypes.string,
    user: PropTypes.object,
    attachments: PropTypes.array
};

export default Message;
