import { API_URL } from "../config";

export const imageUrl = (path: string) => {
  try {
    return `${API_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  } catch (error) {
    console.log(error);
  }
};
