import axios from "axios";
import { API_URL } from "../config";

axios.defaults.withCredentials = true;
const api = axios.create({
  baseURL: API_URL,
});

export const imageUrl = (path: string) => {
  try {
    return `${API_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  } catch (error) {
    console.log(error);
    console.log(API_URL, path);
  }
};

export default api;
