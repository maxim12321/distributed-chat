import React, {useState, useEffect} from "react";
import {connect} from "react-redux";

import {Dialogs as BaseDialogs} from "../components";
import {dialogsActions} from "../redux/actions";

const Dialogs = ({items, fetchDialogs, setCurrentDialogId}) => {
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
        const interval = setInterval(() => {
            if (inputValue.trim().length === 0) {
                fetchDialogs();
                setFilteredItems(items);
            } else {
                // setFilteredItems(items);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, [items, inputValue]);

    return (
        <BaseDialogs
            items={filtered}
            onSearch={onChangeInput}
            inputValue={inputValue}
            onSelectDialog={setCurrentDialogId}
        />
    );
};

export default connect(
    ({dialogs}) => dialogs,
    dialogsActions
)(Dialogs);
