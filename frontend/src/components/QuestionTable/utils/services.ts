import api from "../../../api/client";
import type { AxiosError } from "axios";

type CodeRunResponse = {
  success: boolean;
  error: string | null;
  quiz_response: Record<string, any>;
  http_status_code: string;
};
type RunTestItem = {
  question_id: number;
  server_type: "python" | "javascript";
  status: "ok" | "error";
  output: CodeRunResponse;
};
type RunTestResponse = {
  success_count: number;
  failure_count: number;
  results: RunTestItem[];
};

export type MinimalTestResult = {
  idx: string;
  status: "ok" | "error";
  pass: number;
};

export async function runQuestionTest(
  questions_ids: string[]
): Promise<MinimalTestResult[]> {
  try {
    const controller = new AbortController();
    const signal = controller.signal;
    const response = await api.post<RunTestResponse>(
      "/db_questions/run_test/",
      {
        questions_id: questions_ids,
        server_type: "javascript",
      },
      { signal: signal }
    );

    const data = response.data;
    if (!data || !Array.isArray(data.results)) return [];

    const testData = data.results;

    const testResults: MinimalTestResult[] = testData.map((item) => ({
      idx: String(item.question_id),
      status: item.status,
      pass: Number(item.output?.quiz_response?.test_results?.pass ?? 0),
    }));
    return testResults;
  } catch (error: any) {
    const e = error as AxiosError;
    console.error(
      "[runQuestionTest] request failed",
      e.response?.status,
      e.response?.data ?? e.message
    );
    throw e;
  }
}

export function filenameFromDisposition(
  cd?: string | null,
  fallback = "questions.zip"
) {
  if (!cd) return fallback;
  // Handles: filename="name.zip" and RFC5987 filename*=UTF-8''name.zip
  const m = /filename\*?=(?:UTF-8''|")?([^\";]+)"?/i.exec(cd);
  try {
    return m?.[1] ? decodeURIComponent(m[1]) : fallback;
  } catch {
    return fallback;
  }
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function downloadQuestions(
  ids: string[],
  opts?: {
    signal?: AbortSignal;
    onProgress?: (pct: number) => void;
    filename?: string;
  }
): Promise<void> {
  if (!ids.length) return;

  const {
    signal,
    onProgress,
    filename: fallbackName = "question.zip",
  } = opts ?? {};

  for (let i = 0; i < ids.length; i++) {
    const qid = ids[i];

    const res = await api.post(
      `/questions/${encodeURIComponent(qid)}/download`, // <-- matches your route
      null, // no body, qid is in path
      {
        responseType: "blob",
        signal,
        onDownloadProgress: (e) => {
          if (onProgress && e.total) {
            const pct = Math.round((e.loaded / e.total) * 100);
            onProgress(pct);
          }
        },
      }
    );

    const blob: Blob = res.data;

    // If server responded with JSON instead of zip, surface error
    if (blob.type && blob.type.includes("application/json")) {
      const text = await blob.text();
      try {
        const err = JSON.parse(text);
        throw new Error(err.detail || err.message || "Download failed");
      } catch {
        throw new Error(text || "Download failed");
      }
    }

    const cd = res.headers["content-disposition"] as string | undefined;
    const fileName = filenameFromDisposition(cd, `${qid}-${fallbackName}`);

    downloadBlob(blob, fileName);
  }
}
