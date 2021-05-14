import {axios} from "../../core";

export default {
    getAll: () => axios.get("/get_chat_id_list")
};
