import api from "./client";
import type { QuestionMeta } from "../types/types";
import { toast } from "react-toastify";
import type { QuestionFormData } from "../types/types";
import type { Question, QuestionFull, FileName } from "../types/questionTypes";
import type { FileData } from "../types/types";
type searchQuestionProps = {
  filter?: QuestionMeta;
  showAllQuestions: boolean;
};

type SyncMetrics = {
  total_found: number;
  synced: number;
  skipped: number;
  failed: number;
};

type SyncResponse = {
  metrics: SyncMetrics;
  syncedQuestions: Question[];
  skippedQuestions: any[]; // There is a different type but forget for now
  failedQuestions: string[];
};

type FolderCheckMetrics = {
  total_checked: number;
  deleted_from_db: number;
  still_valid: number;
};

type PruneResponse = {
  metrics: FolderCheckMetrics;
  remaining_questions: Question[];
};

type FileDataResponse = {
  status: number;
  detail: string;
  filedata: FileData[];
  filepaths: string[];
};

export const questionApi = {
  async getbyId(id: string): Promise<Question> {
    const res = await api.get(`/questions/${encodeURIComponent(id)}`);
    return res.data.question;
  },
  async getbyIdFull(id: string): Promise<QuestionFull> {
    const res = await api.get(`/questions/${encodeURIComponent(id)}/full`);
    return res.data;
  },

  async getFileNames(id: string): Promise<FileName> {
    const res = await api.get(`/questions/${encodeURIComponent(id)}/files`);
    return res.data;
  },
  async uploadFiles(id: string, files: File[]): Promise<GeneralResponse> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    const res = await api.post(
      `/questions/${encodeURIComponent(id)}/files`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return res.data;
  },

  async readQuestionFile(
    id: string,
    filename: string
  ): Promise<GeneralDataResponse> {
    const response = await api.get<SuccessDataResponse>(
      `/questions/${encodeURIComponent(id)}/files/${encodeURIComponent(
        filename
      )}`
    );
    return response.data;
  },

  async getAllQuestions(offset: number, limit: number): Promise<Question[]> {
    const response = await api.get<Question[]>(
      `/questions/get_all/${offset}/${limit}/minimal`
    );
    return response.data;
  },
  async filterQuestions({
    filter,
    showAllQuestions,
  }: searchQuestionProps): Promise<Question[]> {
    if (showAllQuestions) {
      return await questionApi.getAllQuestions(0, 100);
    } else {
      const response = await api.post(
        "/questions/filter_questions",
        !showAllQuestions ? filter : {}
      );
      return response.data;
    }
  },
  async SyncQuestions(): Promise<SyncResponse> {
    const response = await api.post("/questions/sync_questions");
    return response.data;
  },
  async PruneQuestions(): Promise<PruneResponse> {
    const response = await api.post("/questions/prune_missing_questions");
    return response.data;
  },

  async getQuestionFiles({
    questionID,
  }: {
    questionID: string;
  }): Promise<FileData[]> {
    const response = await api.get<FileDataResponse>(
      `/questions/${questionID}/files_data`
    );
    return response.data.filedata;
  },
  async saveFileContent(
    filename: string,
    content: string,
    id: string | null
  ): Promise<boolean> {
    await api.put("/questions/update_file", {
      question_id: id,
      filename,
      new_content: content,
    });
    toast.success("Code Saved Successfully");
    return true;
  },
};

export const searchQuestions = async ({
  filter,
  showAllQuestions = true,
}: searchQuestionProps) => {
  let retrievedQuestions: any[] = [];
  try {
    const data = await api.post(
      "/questions/filter_questions",
      !showAllQuestions ? filter : {}
    );
    retrievedQuestions = data.data || [];
    return retrievedQuestions;
  } catch (error) {
    console.error(
      "There was an error retrieving the questions returning an empty list",
      error
    );
    return [];
  }
};

import type {
  SuccessDataResponse,
  SuccessFileResponse,
} from "../types/responseModels";
import type {
  GeneralDataResponse,
  GeneralResponse,
} from "../types/responseTypes";

type Settings = {
  storage_type: "cloud" | "local";
};
export const getSettings = async () => {
  try {
    const response = await api.get<Settings>("/settings");
    return response.data.storage_type;
  } catch (error) {
    console.error("Could not fetch question settings", error);
  }
};

export const downloadStart = async () => {
  try {
    const data = await api.post("/questions/download_starter");
    console.log(data);
  } catch (error) {
    console.log("There was an error", error);
    toast.error("Could not download Starter Template");
  }
};
export async function getQuestionFile(questionId: string, filename: string) {
  if (!questionId) return;
  try {
    const response = await api.get<SuccessDataResponse>(
      `/questions/${encodeURIComponent(questionId)}/files/${encodeURIComponent(
        filename
      )}`
    );
    console.log("This is the response of getting the files", response);
    return response.data.data;
  } catch (error) {
    console.log("Could not get question file ", error);
  }
}

export async function getQuestionHTML(questionId: string) {
  const data = await getQuestionFile(questionId, "question.html");
  console.log("This is the question html", data);
  return data;
}
export async function getSolutionHTML(questionId: string) {
  return await getQuestionFile(questionId, "solution.html");
}

export async function deleteQuestions(ids: string[]): Promise<void> {
  if (!ids.length) return;
  await Promise.all(ids.map((id) => api.delete(`/questions/${id}`)));
}

export async function getFiles(id: string) {
  try {
    const res = await api.get<SuccessFileResponse>(
      `/questions/${encodeURIComponent(id)}/files_data`
    );
    console.log("This is the response", res);
    return Array.isArray(res.data.files) ? res.data.files : [];
  } catch (error) {
    console.log(error);
    return [];
  }
}

export async function saveFileContent(
  filename: string,
  content: string,
  id: string
): Promise<boolean> {
  try {
    const result = await api.put("/questions/update_file", {
      question_id: id,
      filename,
      new_content: content,
    });
    toast.success("Code Saved Successfully");
    console.log(result);

    return true;
  } catch (err) {
    console.error("Error saving file content:", err);
    toast.error("Code Not Saved");
    return false;
  }
}

type QuestionFormInput = QuestionFormData & { files?: File[] };
export async function createQuestion({
  title,
  isAdaptive,
  createdBy,
  ai_generated,
  topics,
  languages,
  qtypes,
  files,
}: QuestionFormInput) {
  try {
    const qData = {
      title: title,
      ai_generated: ai_generated
        ? ai_generated.toLowerCase() === "true"
        : false,
      isAdaptive: isAdaptive ? isAdaptive.toLowerCase() === "true" : false,
      createdBy: createdBy,
    };
    const additionalMeta = {
      topics: topics,
      languages: languages,
      qtypes: qtypes,
    };

    const formData = new FormData();
    formData.append("question", JSON.stringify(qData));
    formData.append("additional_metadata", JSON.stringify(additionalMeta));

    if (files) {
      files.forEach((file) => {
        formData.append("files", file, file.name);
      });
    }

    const response = await api.post(
      "/file_uploads/create_question/upload",
      formData
    );
    console.log(response);
    toast.success("Question created succesfully");
  } catch (error) {
    console.log(error);
  }
}
