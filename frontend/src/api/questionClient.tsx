import { useState, useCallback, useEffect, useRef } from "react";

import type { QuestionMeta } from "../types/types";
import type { QuestionParams } from "../types/types";

import api from "./api";

type searchQuestionProps = {
    filter?: QuestionMeta;
    showAllQuestions: boolean;
};

export const searchQuestions = async ({
    filter,
    showAllQuestions,
}: searchQuestionProps) => {
    let retrievedQuestions = [];
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

export function getQuestionMeta(selectedQuestion?: string | null): any {
    const [data, setData] = useState<QuestionMeta | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    //   Resets all the data
    const reset = useCallback(() => {
        setData(null);
        setError(null);
        setLoading(false);
    }, []);

    useEffect(() => {
        if (!selectedQuestion) {
            reset();
            return;
        }

        const controller = new AbortController();
        (async () => {
            try {
                setLoading(true);
                setError(null);
                const res = await api.get(
                    `/question_crud/get_question_data_meta/${encodeURIComponent(
                        selectedQuestion
                    )}`,
                    { signal: controller.signal }
                );

                const qData =
                    typeof res.data.question === "string" ? JSON.parse(res.data.question) : res.data.question;
                setData(qData);
            } catch (error: any) {
                if (error?.name !== "CanceledError") {
                    setError("Could not get question data");
                }
            } finally {
                setLoading(false);
            }
        })();
        return () => controller.abort();
    }, [selectedQuestion, reset]);

    return { data, loading, error, reset };
}


export async function getQuestionHTML(questionId: string) {
    if (!questionId) return;
    try {
        const response = await api.get(
            `/question_crud/get_question/${encodeURIComponent(
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
            `/question_crud/get_question/${encodeURIComponent(
                questionId
            )}}/file/solution.html`
        );
        return response.data.content;
    } catch (error) {
        console.log(error);
    }
}


export function getAdaptiveParams(
    selectedQuestion: string | null | undefined,
    codeLanguage: "python" | "javascript",
    enabled: boolean
) {
    const [params, setParams] = useState<QuestionParams | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const abortRef = useRef<AbortController | null>(null);
    const reset = useCallback(() => {
        if (!enabled || !selectedQuestion) {
            setParams(null);
            setError(null);
            setLoading(false);
            return;
        }
        abortRef.current?.abort();
        const controller = new AbortController();
        abortRef.current = controller;
        (async () => {
            try {
                setLoading(true);
                setError(null);
                const res = await api.post(
                    `/question_running/run_server/${encodeURIComponent(
                        selectedQuestion
                    )}/${encodeURIComponent(codeLanguage)}`,
                    undefined,
                    { signal: controller.signal }
                );
                if (!res.data.success) {
                    console.log("this is the error", res.data.error);
                    setError(res.data.error);
                    return;
                }

                const pData = res?.data?.quiz_response ?? null;
                if (!pData) {
                    const raw = res?.data?.error || res?.data?.quiz_response?.error;
                    throw new Error(
                        typeof raw === "object"
                            ? JSON.stringify(raw)
                            : String(raw ?? "Unknown error")
                    );
                }
                setParams(pData);
            } catch (e: any) {
                if (e?.name !== "CanceledError")
                    setError("Could not generate question data");
            } finally {
                setLoading(false);
            }
        })();
        return () => controller.abort();
    }, [enabled, selectedQuestion, codeLanguage]);

    useEffect(() => {
        void reset();
        return () => abortRef.current?.abort();
    }, [reset]);

    return { params, loading, error, reset };
}


export async function deleteQuestions(ids: string[]): Promise<void> {
    if (!ids.length) return;
    await Promise.all(
        ids.map((id) => api.delete(`/question_crud/delete_question/${id}`))
    );
}
