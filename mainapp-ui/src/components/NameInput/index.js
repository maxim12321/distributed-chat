import React, {useState} from "react";

import "./NameInput.scss";
import {UserOutlined} from "@ant-design/icons";
import {Form, Input} from "antd";
import {Button} from "../index";

const NameInput = props => {
    const [value, setValue] = useState("");
    const {onSendMessage} = props

    const sendInput = (e) => {
        if (e.keyCode === 13) {
            sendUserName();
        }
    }

    const sendUserName = () => {
        if (value.trim() !== "") {
            onSendMessage(value);
        }
    }

    return (
        <Form className="login-form">
            <Form.Item>
                <Input
                    prefix={
                        <UserOutlined style={{opacity: "0.5"}}/>
                    }
                    size="large"
                    placeholder="Username"
                    onKeyUp={sendInput}
                    onChange={e => setValue(e.target.value)}
                    value={value}
                />
            </Form.Item>
            <Form.Item>
                <Button className="thi_button" type="primary" size="large" onClick={sendUserName}>
                    зайти в соцсеть
                </Button>
            </Form.Item>
        </Form>
    )
};

export default NameInput;
