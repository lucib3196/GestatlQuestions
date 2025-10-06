import type { QuestionParams } from "../../types/types";

type showAnswerProps = {
  questionParams: QuestionParams | null;
};

function normalizeValue(v: any) {
  if (typeof v === "boolean") return v ? "True" : "False";
  if (Array.isArray(v)) return v.join(", ");
  if (v && typeof v === "object") return JSON.stringify(v);
  return String(v ?? "");
}

function formatCorrectAnswers(params: QuestionParams | null) {
  const correctAnswers = Object.entries(params?.correct_answers ?? {});
  return (
    <div className="">
      {correctAnswers.map(([key, value]) => (
        <li
          key={key}
          className="flex items-start justify-between gap-3 px-4 py-2"
        >
          <span className="font-mono">{key}</span>
          <span className="shrink-0 inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
            {normalizeValue(value)}
          </span>
        </li>
      ))}
    </div>
  );
}
function DisplayCorrectAnswer({ questionParams }: showAnswerProps) {
  return (
    <div className="w-full mt-3 rounded-xl border">
      <div className="px-4 py-2 border-b font-semibold">
        <span className="font-medium">Answer:</span>{" "}
      </div>
      {formatCorrectAnswers(questionParams)}
    </div>
  );
}

export default DisplayCorrectAnswer;
