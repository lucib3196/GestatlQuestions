import type {
  QuestionBase,
  QuestionData,
  QuestionMeta,
} from "../../types/questionTypes";
import type { SuccessDataResponse } from "../../types/responseModels";

import api from "../client";

export class QuestionAPI {
  private static readonly base = "/questions";

  /** Create a new question */
  static async create(payload: QuestionData): Promise<QuestionBase> {
    const response = await api.post(this.base, payload);
    return response.data;
  }

  /** Delete all questions (use carefully) */
  static async deleteAll(): Promise<any> {
    const response = await api.delete(this.base);
    return response.data;
  }

  /** Get paginated questions */
  static async getAll(offset: number, limit: number): Promise<QuestionBase[]> {
    const response = await api.get(`${this.base}/${offset}/${limit}`);
    return response.data;
  }

  /** Get a question (full data) by ID */
  static async getQuestion(id: string | number): Promise<QuestionBase> {
    const response = await api.get(`${this.base}/${encodeURIComponent(id)}`);
    return response.data;
  }

  /** Get question metadata only by ID */
  static async getQuestionMeta(id: string | number): Promise<QuestionMeta> {
    const response = await api.get(
      `${this.base}/${encodeURIComponent(id)}/meta`
    );
    return response.data;
  }

  /** Get all question metadata (paginated) */
  static async getAllQuestionsMeta(
    offset: number,
    limit: number
  ): Promise<QuestionMeta[]> {
    const response = await api.get(`${this.base}/${offset}/${limit}/all_data`);
    return response.data;
  }

  /** Delete a specific question by ID */
  static async deleteQuestion(id: string | number): Promise<any> {
    const response = await api.delete(`${this.base}/${encodeURIComponent(id)}`);
    return response.data;
  }

  /** Update an existing question by ID */
  static async updateQuestion(
    id: string | number,
    updatePayload: QuestionData
  ): Promise<QuestionMeta> {
    const response = await api.put(
      `${this.base}/${encodeURIComponent(id)}`,
      updatePayload
    );
    return response.data;
  }

  /** Filter questions by given criteria */
  static async filterQuestions(filter: QuestionData): Promise<QuestionMeta[]> {
    const response = await api.post(`${this.base}/filter`, filter);
    return response.data;
  }

  static async getQuestionFile(
    questionId: string,
    filename: string
  ): Promise<SuccessDataResponse> {
    const response = await api.get(
      `${this.base}/files/${encodeURI(questionId)}/${encodeURIComponent(
        filename
      )}`
    );
    return response.data;
  }
}
