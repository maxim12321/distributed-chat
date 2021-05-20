import axios from "axios";
axios.defaults.baseURL = "http://localhost:" + process.env.REACT_APP_BACKEND_PORT;
export default axios;
