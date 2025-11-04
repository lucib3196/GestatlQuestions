import api from "./client";
import type {
  UnsyncedQuestion,
  SyncMetrics,
  FolderCheckMetrics,
} from "../types/syncTypes";

export class QuestionSyncAPI {
  private static readonly base = "/questions";

  static async checkSync(): Promise<UnsyncedQuestion[]> {
    const response = await api.post(`${this.base}/check_unsync`);
    return response.data;
  }
  static async SyncQuestions(): Promise<SyncMetrics> {
    const response = await api.post(`${this.base}/sync_questions`);
    return response.data;
  }
  static async PruneMissingQuestions(): Promise<FolderCheckMetrics> {
    const response = await api.post(`${this.base}/prune_missing_questions`);
    return response.data;
  }
}
