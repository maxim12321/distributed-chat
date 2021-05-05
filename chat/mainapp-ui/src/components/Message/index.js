import React from "react";
import PropTypes from "prop-types";
import classNames from "classnames";

import "./Message.scss";

const Message = ({ avatar, user, text, date, isMe, attachments }) => (
  <div className={classNames('message', {
      'message--isme' : isMe,
      'message--image' : attachments && attachments.length === 1
    })}
  >
    <div className="message__content">
      <div className="message__avatar">
        <img src={avatar} alt={`Avatar ${user.fullname}`} />
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
                <img src={item.url} alt={item.filename} />
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