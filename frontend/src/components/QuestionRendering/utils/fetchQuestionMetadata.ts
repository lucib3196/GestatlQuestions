import { useEffect, useState, useCallback } from "react";
import api from "../../../api";
import type { QuestionMetadata } from "../../../types/types";

export function useQuestionMeta(selectedQuestion?: string | null): any {
  const [data, setData] = useState<QuestionMetadata | null>(null);
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
          `/db_questions/get_question/qmeta/${encodeURIComponent(
            selectedQuestion
          )}`,
          { signal: controller.signal }
        );

        const qData =
          typeof res.data === "string" ? JSON.parse(res.data) : res.data;
        console.log("This is the qQata", qData)
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
