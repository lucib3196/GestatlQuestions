// questionApi.ts
import api from "./api";
import type { QuestionMeta } from "../types/types";
import { toast } from "react-toastify";

type searchQuestionProps = {
  filter?: QuestionMeta;
  showAllQuestions: boolean;
};

export const searchQuestions = async ({
  filter,
  showAllQuestions,
}: searchQuestionProps) => {
  let retrievedQuestions: any[] = [];
  try {
    const data = await api.post(
      "/question_crud/filter_questions/",
      !showAllQuestions ? filter : {}
    );
    retrievedQuestions = data.data || [];
    return retrievedQuestions;
  } catch (error) {
    console.log(error);
  }
};

export async function getQuestionHTML(questionId: string) {
  if (!questionId) return;
  try {
    const response = await api.get(
      `/question_crud/get_question/${encodeURIComponent(
        questionId
      )}}/file/question.html` // kept as-is (note the double `}}`)
    );
    return response.data.content;
  } catch (error) {
    console.log(error);
  }
}

export async function getSolutionHTML(questionId: string) {
  if (!questionId) return;
  try {
    const response = await api.get(
      `/question_crud/get_question/${encodeURIComponent(
        questionId
      )}}/file/solution.html` // kept as-is (note the double `}}`)
    );
    return response.data.content;
  } catch (error) {
    console.log(error);
  }
}

export async function deleteQuestions(ids: string[]): Promise<void> {
  if (!ids.length) return;
  await Promise.all(
    ids.map((id) => api.delete(`/question_crud/delete_question/${id}`))
  );
}

export async function getFiles(id: string) {
  try {
    const res = await api.get(
      `/question_crud/get_question/${encodeURIComponent(id)}/get_all_files`
    );
    console.log("these are all the files");
    console.log(res.data.files);
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
    const result = await api.post("/question_crud/update_file_content", {
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
