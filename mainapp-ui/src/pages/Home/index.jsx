import React from "react";
import {Messages, Sidebar} from "../../containers";
import "./Home.scss";

const Home = () => (
    <section className="home">
        <div className="chat">
            <Sidebar/>
            <Messages/>
        </div>
    </section>
)

export default Home;
