import type { User } from "firebase/auth";
import { getIdToken } from "firebase/auth";
import api from "./client";

export class UserAPI {
  private static readonly base = "/user";

  static async getCurrentUser(token: string) {
    const response = await api.get(this.base, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    console.log("[Frontend] User fetched:");
    return response.data;
  }
  static async createUser(
    username: string,
    user: User
  ): Promise<boolean | undefined> {
    const token = await getIdToken(user);
    const response = await api.post<boolean>(
      "/user",
      { username },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  }
}
