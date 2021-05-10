import React, { useState, useEffect } from "react";
import { connect } from "react-redux";

import { Dialogs as BaseDialogs } from "../components";
import { dialogsActions } from "../redux/actions";

const Dialogs = ({ fetchDialogs, setCurrentDialogId, items, userId }) => {
  const [inputValue, setValue] = useState("");
  const [filtered, setFilteredItems] = useState(Array.from(items));

  const onChangeInput = value => {
    setFilteredItems(
      items.filter(
        dialog => dialog.user.fullname.toLowerCase().indexOf(value.toLowerCase()) >= 0
      )
    );
    setValue(value);
  };

  useEffect(() => {
    if (!items.length){
      fetchDialogs();
    } else {
      setFilteredItems(items);
    }
  }, [items]);

  return(
    <BaseDialogs
      userId={userId}
      items={filtered}
      onSearch={onChangeInput}
      inputValue={inputValue}
      onSelectDialog={setCurrentDialogId}
      />
  );
};

export default connect(
  ({ dialogs }) => dialogs,
  dialogsActions
)(Dialogs);