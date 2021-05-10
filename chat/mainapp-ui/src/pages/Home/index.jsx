import React from "react";
import { ChatInput } from "../../components";
import { Dialogs, Messages } from "../../containers";
import "./Home.scss";

const Home = () => (
  <section className="home">
    <div className="chat">
      <div className="chat__sidebar">
        <div className="chat__sidebar-header">
          <div>
            <span>Список диалогов</span>
          </div>
        </div>
        <div className="chat__sidebar-dialogs">
          <Dialogs  />
        </div>
      </div>
      <div className="chat__dialog">
        <div className="chat__dialog-header">
          <div className="chat__dialog-header-center">
            <b className="chat__dialog-header-username"> Оля Войтович </b>
          </div>
        </div>
        <div className="chat__dialog-messages">
          <Messages />
        </div>
        <div className="chat__dialog-input">
            <ChatInput />
        </div>
      </div>
    </div>
  </section>
)

export default Home;