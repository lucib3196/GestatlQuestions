export type SuccessResponse = {
  status: number;
  detail: string;
};

export type SuccessDataResponse = SuccessResponse & {
  data: string;
};

export type FileData = {
  filename: string;
  content: any;
};
export type SuccessFileResponse = SuccessResponse & {
  files: FileData[];
  filepaths?: string[];
};
