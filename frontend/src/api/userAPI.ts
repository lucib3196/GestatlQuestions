import type { User } from "firebase/auth";
import { getIdToken } from "firebase/auth";
import api from "./client";

type UserRole = "admin" | "teacher" | "developer" | "student";

type UserDB = {
  id?: string;
  username?: string;
  email?: string;
  role?: UserRole;
  fb_id?: string;
  storage_path?: string;
};

export class UserAPI {
  private static readonly base = "/user";

  static async getCurrentUser(token: string): Promise<UserDB> {
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
    email: string,
    user: User
  ): Promise<UserDB> {
    const token = await getIdToken(user);
    const data: UserDB = {
      email: email,
      fb_id: token,
      username: username,
    };
    const response = await api.post<UserDB>(
      "/user",
      { data },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  }

  static async getUser(id: string): Promise<UserDB> {
    const response = await api.get<UserDB>(
      `${this.base}/${encodeURIComponent(id)}`
    );
    return response.data;
  }
  static async deleteUser(id: string): Promise<UserDB> {
    const response = await api.delete(`${this.base}/${encodeURIComponent(id)}`);
    return response.data;
  }
  static async updateUser(id: string, data: UserDB): Promise<UserDB> {
    const response = await api.put(
      `${this.base}/${encodeURIComponent(id)}`,
      data
    );
    return response.data;
  }
}
