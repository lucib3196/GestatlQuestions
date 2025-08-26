import api from "../../../api";

export async function getQuestionHTML(questionId: string) {
  if (!questionId) return;
  try {
    const response = await api.get(
      `/db_questions/get_question/${encodeURIComponent(
        questionId
      )}}/file/question.html`
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
      `/db_questions/get_question/${encodeURIComponent(
        questionId
      )}}/file/solution.html`
    );
    return response.data.content;
  } catch (error) {
    console.log(error);
  }
}
