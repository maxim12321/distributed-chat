import React, {useState} from "react";
import {Dialogs} from "../../containers";
import {Modal, Button} from "antd";
import {PlusSquareOutlined} from '@ant-design/icons';

import plus_dialog from '../../resources/plus_dialog.png';

import "./Sidebar.scss";

// <Button shape="circle" icon={<PlusSquareOutlined />} onClick={() => setVisible(true)}/>

const Sidebar = ({user}) => {
    const [visible, setVisible] = useState(false);

    const onClose = () => {
        // TODO: Create chat
        setVisible(false);
    }

    return (
        <div className="chat__sidebar">
            <div className="chat__sidebar-header">
                <span className="chat__sidebar-header-list">Список диалогов</span>
                <img className="chat__sidebar-header-add" src={plus_dialog} alt="plus_dialog"
                     onClick={() => setVisible(true)}/>
            </div>
            <div className="chat__sidebar-dialogs">
                <Dialogs/>
            </div>
            <Modal className="chat__sidebar-modal" title="Создать диалог" visible={visible} onOk={onClose}
                   onCancel={onClose}>
                <input
                    className="chat__sidebar-modal-input"
                    type='text'
                    placeholder="Введите название нового диалога"/>
            </Modal>
        </div>
    );
};

export default Sidebar;