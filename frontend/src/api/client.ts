import axios from "axios";
import { API_URL } from "../config";

axios.defaults.withCredentials = true;
const api = axios.create({
  baseURL: API_URL,
});

export default api;
