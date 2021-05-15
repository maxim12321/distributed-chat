import React, {useState} from "react";
import {Dialogs} from "../../containers";
import {Modal} from "antd";

import plus_dialog from '../../resources/plus_dialog.png';

import "./Sidebar.scss";

const Sidebar = ({getNetworkInviteLink, sendChatName}) => {
    const [visible, setVisible] = useState(false);
    const [value, setValue] = useState("");
    const [inviteLink, setInviteLink] = useState("");

    const onClose = () => {
        if (value.trim() !== "") {
            setValue("")
            setVisible(false);
            sendChatName(value)
        }
    }

    const updateInviteLink = () => {
        console.log("Hi")
        console.log(getNetworkInviteLink())
        getNetworkInviteLink().then(response => setInviteLink(response.data))
        return (
            <a onClick={() => navigator.clipboard.writeText(inviteLink)}>
                Скопировать ссылку в сеть
            </a>
        )
    }

    return (
        <div className="chat__sidebar">
            <div className="chat__sidebar-invite">
                {updateInviteLink()}
            </div>
            <div className="chat__dialogs">
                <div className="chat__sidebar-header">
                    <span className="chat__sidebar-header-list">Список диалогов</span>
                    <img className="chat__sidebar-header-add" src={plus_dialog} alt="plus_dialog"
                         onClick={() => setVisible(true)}/>
                </div>
                <div className="chat__sidebar-dialogs">
                    <Dialogs/>
                </div>
                <Modal className="chat__sidebar-modal" title="Создать диалог" visible={visible} onOk={onClose}
                       onCancel={() => setVisible(false)}>
                    <input
                        className="chat__sidebar-modal-input"
                        type='text'
                        placeholder="Введите название нового диалога"
                        onChange={e => setValue(e.target.value)}
                        value={value}
                    />
                </Modal>
            </div>
        </div>
    );
};

export default Sidebar;
