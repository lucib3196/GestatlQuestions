import { useCallback, useEffect, useState, useRef } from "react";
import api from "../../../api";
import type { QuestionParams } from "../../../types/types";

export function useAdaptiveParams(
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
          `/db_questions/run_server/${encodeURIComponent(
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
