import React from "react";
import dialogs_empty from '../../resources/dialogs_empty.png';

import "./Dialogs.scss";
import {DialogItem} from "../"

const Dialogs = ({items, onSearch, inputValue, onSelectDialog}) => (
    <div className="dialogs">
        <div className="chat__sidebar-search">
            <input
                type='text'
                placeholder="Поиск"
                onChange={e => onSearch(e.target.value)}
                value={inputValue}
            />
        </div>
        {(items.length) ? (items.map(item => (
            <DialogItem
                _id={item._id}
                user={item.user}
                message={item.message}
                onSelect={onSelectDialog}
            />
        ))) : (
            <div className="dialogs-empty">
                <img className="dialogs-empty-image" src={dialogs_empty} alt="dialogs_empty"/>
                <p>Не найдено активных диалогов</p>
            </div>
        )}
    </div>
);

export default Dialogs;
