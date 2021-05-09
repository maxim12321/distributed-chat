import React from "react";
import { Messages, Dialogs, ChatInput } from "../../components";
import add_image from '../../resources/add_image.png';
import "./Home.scss";


import dialogsJSON from "../../dialogs.json";

const Home = () => (
  <section className="home">
    <div className="chat">
      <div className="chat__sidebar">
        <div className="chat__sidebar-header">
          <div>
            <span>Список диалогов</span>
          </div>
        </div>
        <div className="chat__sidebar-search">
           <input type='text' placeholder="Поиск" />
        </div>
        <div className="chat__sidebar-dialogs">
          <Dialogs items={dialogsJSON} />
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