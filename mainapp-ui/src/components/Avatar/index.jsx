import React from "react";
import PropTypes from "prop-types";

import "./Avatar.scss";

const Avatar = ({user}) => {
    if (user.avatar) {
        return (
            <img
                className="avatar"
                src={user.avatar}
                alt={`Avatar ${user.fullname}`}
            />
        );
    } else {
        const firstChar = user.fullname[0].toUpperCase();
        return (
            <div
                style={{
                    background: `linear-gradient(#a8dadc, #457b9d)`
                }}
                className="avatar avatar--symbol"
            >
                {firstChar}
            </div>
        );
    }
};

Avatar.propTypes = {
    className: PropTypes.string
};

export default Avatar;
