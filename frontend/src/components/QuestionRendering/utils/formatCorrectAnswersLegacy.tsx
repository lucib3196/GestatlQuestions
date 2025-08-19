// helpers inside your component:
import type { QuestionParams } from "../../../types/types";
const formatValue = (v: any) => {
    if (typeof v === "boolean") return v ? "True" : "False";
    if (Array.isArray(v)) return v.join(", ");
    if (v && typeof v === "object") return JSON.stringify(v);
    return String(v ?? "");
};

const formatCorrectAnswers = (params: QuestionParams) => {
    const entries = Object.entries(params?.correct_answers ?? {});

    if (entries.length === 0) {
        return (
            <div className="rounded-lg border border-slate-200 bg-slate-50 text-slate-700 px-4 py-3 text-sm">
                No correct answers available.
            </div>
        );
    }

    return (
        <div className="mt-3 rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="px-4 py-2 border-b border-slate-200 text-slate-700 font-semibold">
                Correct Answers
            </div>

            <ul className="divide-y divide-slate-200">
                {entries
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([key, value]) => (
                        <li key={key} className="flex items-start justify-between gap-3 px-4 py-2">
                            <span className="text-sm text-slate-600">
                                <span className="font-medium">Answer:</span>{" "}
                                <span className="font-mono text-slate-800">{key}</span>
                            </span>

                            <span className="shrink-0 inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                                {formatValue(value)}
                            </span>
                        </li>
                    ))}
            </ul>
        </div>
    );
};

const showCorrectAnswer = (isSubmitted: boolean, params: QuestionParams | null) => {
    if (!isSubmitted || !params) return null;
    return (
        <div className="mt-4">
            <div className="mb-2 text-sm text-slate-600">Answer submitted ✅</div>
            {formatCorrectAnswers(params)}
        </div>
    );
};


export default showCorrectAnswer