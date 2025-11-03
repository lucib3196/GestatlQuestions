import type { QuestionBase, QuestionData } from "../../types/questionTypes";
import type { QuestionMeta } from "../../types/types";

import api from "../client";

export class QuestionAPI {
  private static base = "/questions";

  static async create(payload: QuestionData): Promise<QuestionBase> {
    const response = await api.post(`${this.base}`, {
      question: payload,
    });
    return response.data;
  }
  static async delete() {
    const response = await api.delete(this.base);
    return response.data;
  }
  static async get_all(offset: number, limit: number): Promise<QuestionBase[]> {
    const response = await api.get(`${this.base}/${offset}/${limit}`);
    return response.data;
  }
  static async get_question(id: string | number): Promise<QuestionBase> {
    const response = await api.get(`${this.base}/${encodeURIComponent(id)}`);
    return response.data;
  }
  static async get_question_meta(id: string | number): Promise<QuestionMeta> {
    const response = await api.get(`${this.base}/${encodeURIComponent(id)}`);
    return response.data;
  }
  static async get_all_questions_meta(
    offset: number,
    limit: number
  ): Promise<QuestionMeta[]> {
    const response = await api.get(`${this.base}/${offset}/${limit}/all_data`);
    return response.data;
  }
  static async delete_question(id: string | number) {
    const response = await api.delete(`${this.base}/${encodeURIComponent(id)}`);
    return response.data;
  }
  static async update_question(
    id: string | number,
    update_payload: QuestionData
  ): Promise<QuestionMeta> {
    const response = await api.put(`${this.base}/${encodeURIComponent(id)}`, {
      update: update_payload,
    });
    return response.data;
  }

  static async filter_questions(filter: QuestionData): Promise<QuestionMeta[]> {
    const response = await api.post(`${this.base}/filter`, {
      filter: filter,
    });
    return response.data;
  }
}
