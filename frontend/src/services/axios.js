import axios from 'axios';

// Configure Axios
axios.defaults.withCredentials = true;  // Ensure cookies are sent with requests

export default axios;
