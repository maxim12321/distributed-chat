import React from "react";
import { Form, Input, Checkbox } from "antd";
import Icon from '@ant-design/icons';
import { UserOutlined } from '@ant-design/icons';

import { Button, Block } from "../../components";
import "./Login.scss";

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
          <Form onSubmit={this.handleSubmit} className="login-form">
          <Form.Item>
            <Input
              prefix={
               <UserOutlined style={{ opacity: "0.5" }} />
              }
              size="large"
              placeholder="Username"
            />
          </Form.Item>
          <Form.Item>
            <Button className="thi_button" type="primary" size="large">
             зайти в соцсеть
            </Button>
          </Form.Item>
          </Form>
        </Block>
      </div>
    </section>
  )
 }
}

export default Login;