import React from "react";
import dialogs_empty from '../../resources/dialogs_empty.png';

import "./Dialogs.scss";
import { DialogItem } from "../"

const Dialogs = ({ items }) => (
  <div className="dialogs">
    {(items.length) ? (items.map(item => (
      <DialogItem
        user={item.user}
        message={item.message}
      />
    ))) : (
      <div className="dialogs-empty">
        <img className="dialogs-empty-image" src={dialogs_empty}/>
        <p>Не найдено активных диалогов</p>
      </div>
    )}
  </div>
);

export default Dialogs;