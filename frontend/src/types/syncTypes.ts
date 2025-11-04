export type UnsyncedQuestion = {
  question_name: string;
  question_path: string;
  detail: string;
  status: string;
  metadata?: string;
};

export type SyncMetrics = {
  total_found: number;
  synced: number;
  failed: number;
};

export type FolderCheckMetrics = {
  total_checked: number;
  deleted_from_db: number;
  still_valid: number;
  bug?: number;
};
