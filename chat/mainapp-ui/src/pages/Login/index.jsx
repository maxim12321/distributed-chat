import React from "react";
import {Form, Input} from "antd";
import {UserOutlined} from '@ant-design/icons';

import "./Login.scss";
import {Button, Block} from "../../components";
import {NameInput} from "../../containers"

class Login extends React.Component {
    render() {
        return (
            <section className="login">
                <div className="login__content">
                    <div className="login__top">
                        <h2>Войдите в свой аккаунт</h2>
                        <p>Пожалуйста!</p>
                    </div>
                    <Block>
                        <NameInput/>
                    </Block>
                </div>
            </section>
        )
    }
}

export default Login;