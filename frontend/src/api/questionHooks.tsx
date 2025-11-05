// questionHooks.ts
import { useState, useCallback, useEffect, } from "react";
import type { QuestionParams } from "../types/types";
import { useCodeEditorContext } from "../context/CodeEditorContext";
import { QuestionAPI } from "./questionCrud";
import type { QuestionData } from "../types/questionTypes";
import { useQuestionContext } from "../context/QuestionContext";
import { useSelectedQuestion } from "../context/SelectedQuestionContext";



export function useRetrievedQuestions({
  questionFilter,
  showAllQuestions,
}: {
  questionFilter: QuestionData;
  showAllQuestions: boolean;
}) {
  const { setQuestions } = useQuestionContext();
  const fetchQuestions = useCallback(async () => {
    try {
      const filter = showAllQuestions ? {} : questionFilter;
      console.log(filter);
      const retrieved = await QuestionAPI.filterQuestions(questionFilter);
      setQuestions(retrieved);
    } catch (error) {
      console.error("❌ Failed to fetch questions:", error);
    }
  }, [showAllQuestions, questionFilter, setQuestions]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);
}

export function useAdaptiveParams(isAdaptive: boolean) {
  const [params, setParams] = useState<QuestionParams | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { codeRunningSettings, setLogs } = useCodeEditorContext();

  const { selectedQuestionID } = useSelectedQuestion();

  const fetchParams = useCallback(async () => {
    if (!isAdaptive) return;
    if (!selectedQuestionID) return;

    try {
      setLoading(true);
      setError(null);

      const res = await QuestionAPI.runServer(
        selectedQuestionID,
        codeRunningSettings
      );

      setParams(res);
      if (res?.logs) setLogs(res.logs);
    } catch (err: any) {
      console.error("Error fetching adaptive params:", err);
      setError(err?.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [isAdaptive, selectedQuestionID, codeRunningSettings, setLogs]);

  useEffect(() => {
    fetchParams();
  }, [fetchParams]);

  return { params, loading, error, refetch: fetchParams };
}
