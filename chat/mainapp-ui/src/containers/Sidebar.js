import React from "react";
import { connect } from "react-redux";

import { Sidebar } from "../components";

const SidebarContainer = ({ user }) => <Sidebar user={user} />;

export default connect(({user}) => ({ user }))(SidebarContainer);