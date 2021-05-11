import React, { useEffect } from "react";
import { connect } from "react-redux";

import { Messages as BaseMessages } from "../components";
import { messagesActions } from "../redux/actions";

const Dialogs = ({ currentDialogId, lastMessage, fetchMessages, items }) => {
  console.log(currentDialogId)
  useEffect(() => {
  const interval = setInterval(() => {
    if (currentDialogId) {
      fetchMessages(currentDialogId);
    }
  }, 1000);
  return () => clearInterval(interval);
}, [currentDialogId]);

  return <BaseMessages items={items} />;
}

export default connect(
  ({ dialogs, messages }) => ({
    currentDialogId: dialogs.currentDialogId,
    items: messages.items
  }),
  messagesActions
)(Dialogs);