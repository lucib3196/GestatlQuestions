import api from "./client";
import { toast } from "react-toastify";

import type { FileName } from "../types/questionTypes";
import type { FileData } from "../types/types";



type FileDataResponse = {
  status: number;
  detail: string;
  filedata: FileData[];
  filepaths: string[];
};

export const questionApi = {
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
