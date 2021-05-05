import React, { Component } from "react";
import { Route } from "react-router-dom";

import { Login, Home } from "../src/pages";

class App extends Component {
  render() {
    return (
      <div className="wrapper">
        <Route exact path="/" component={ Home } />
      </div>
    );
  }
}

export default App;