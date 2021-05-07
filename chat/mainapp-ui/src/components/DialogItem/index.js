import React from "react";

import "./DialogItem.scss";

const getAvatar = (avatar) => {
  if (avatar) {
    return (
    <img
        src="https://lh3.googleusercontent.com/ogw/ADGmqu_ACEwEWl4pW7gn6u41Z4H6fj64gCMm_zR5KXVqGA=s83-c-mo"
        alt="avatar"
      />
    );
  } else {

  }
}

const DialogItem = ({ user, message }) => (
  <div className="border">
    <div className="dialogs__item">
      <div className="dialogs__item-avatar">
        {getAvatar("d")}
      </div>
      <div className="dialogs__item-info">
        <div className="dialogs__item-info-top">
          <b>Ольга Войтович</b>
          <span>
            13:00
          </span>
        </div>
        <div className="dialogs__item-info-bottom">
          <p>Едем едем в соседнее село на дискотеку со своей фонотекой с гаража угнав</p>
        </div>
      </div>
    </div>
  </div>
);

export default DialogItem;