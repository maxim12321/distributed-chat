import React from "react";

import "./Login.scss";
import {Block} from "../../components";
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
