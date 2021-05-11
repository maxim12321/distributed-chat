import { axios } from "../../core";

export default {
  getAllByDialogId: id => axios.get("/messages?dialog=" + id),
  send: (text) =>
    axios.post("https://httpbin.org/post", {
      text: text
    })
    .then((response) => { console.log(response);})
};
