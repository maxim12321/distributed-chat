import React from "react";
import { Dialogs, Messages, ChatInput, Sidebar } from "../../containers";
import "./Home.scss";

const Home = () => (
  <section className="home">
    <div className="chat">
      <Sidebar />
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