import { useState } from "react";
import { MathJax } from "better-react-mathjax";
import CorrectIndicator from "../../Generic/CorrectIndicator";
import { isCloseEnoug } from "../../../utils/mathHelpers";
import type { NumberInput } from "../../../types/types";
import { useMemo, useId } from "react";
import { roundToSigFigs } from "../../../utils/mathHelpers";

type NumberInputProps = {
    inputData: NumberInput;
    correctAnswers: number;
    isSubmitted: boolean;
};

type AnswerData = {
    numAnswer?: number;
    answerString?: string; // "a: 1, b.c: 2"
    values?: Record<string, string | number | boolean>; // flattened map
};

function formatCorrectAnswer(
    obj: unknown,
    data: Record<string, any>
): AnswerData | string {
    if (obj == null) return "No Answer Provided";

    const out: AnswerData = {
        ...(data as AnswerData),
    };

    const addKV = (key: string, val: string | boolean | number) => {
        (out.values ??= {})[key] = val;

        val = typeof val==="number"? roundToSigFigs(val, 5):val

        out.answerString = out.answerString
            ? `${out.answerString}, ${key}:${String(val)}`
            : `${key}: ${String(val)}`;

        if (typeof val === "number" && out.numAnswer === undefined) {
            out.numAnswer = val;
        }
    };

    const visit = (value: unknown, prefix = "") => {
        if (value == null) return;

        if (
            typeof value === "number" ||
            typeof value === "boolean" ||
            typeof value === "string"
        ) {
            addKV(prefix || "value", value);
            return;
        }
        if (Array.isArray(value)) {
            value.forEach((item, i) =>
                visit(item, prefix ? `${prefix}[${i}]` : String(i))
            );
            return;
        }
        if (typeof value === "object") {
            for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
                visit(v, prefix ? `${prefix}.${k}` : k);
            }
        }
    };
    visit(obj);
    return out;
}

export default function NumberInputDynamic({
    inputData,
    correctAnswers,
    isSubmitted,
}: NumberInputProps) {
    const id = useId();
    const name = inputData.name;
    const displayLabel = inputData.label || name;

    const [submittedAnswer, setSubmittedAnswer] = useState<number | undefined>();

    // Memoize formatting so it only recalculates when correctAnswers changes
    const formatted = useMemo(() => formatCorrectAnswer(correctAnswers, {}), [correctAnswers]);

    
    if (typeof formatted === "string") {
        return (
            <MathJax>
                <fieldset className="border border-gray-300 rounded-lg p-4 mb-4 shadow-sm">
                    <legend className="text-sm font-bold text-gray-700 px-2">Answer</legend>
                    <p className="text-sm text-gray-700">{formatted}</p>
                </fieldset>
            </MathJax>
        );
    }

    const correctNum =
        typeof formatted.numAnswer === "number" ? formatted.numAnswer : undefined;

    // If we don’t have a numeric correct answer, we can’t grade numerically
    // Fall back to showing the answer string (if present).
    const canGrade = correctNum !== undefined;

    const answeredCorrectly =
        isSubmitted && canGrade && submittedAnswer !== undefined
            ? isCloseEnoug(correctNum!, submittedAnswer)
            : false;

    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const n = Number(e.target.value);
        setSubmittedAnswer(Number.isFinite(n) ? n : undefined);
    };

    return (
        <MathJax>
            <fieldset className="border border-gray-300 rounded-lg p-4 mb-4 shadow-sm">
                <legend className="text-sm font-bold text-gray-700 px-2">Answer</legend>

                {/* Input Row */}
                <div className="flex flex-row flex-wrap items-center gap-2">
                    <label htmlFor={id} className="text-sm font-medium text-gray-600">
                        {displayLabel}
                    </label>

                    <input
                        id={id}
                        name={name}
                        type="number"
                        step="any"
                        inputMode="decimal"
                        disabled={isSubmitted}
                        value={submittedAnswer ?? ""}
                        onChange={handleChange}
                        onWheel={(e) => (e.currentTarget as HTMLInputElement).blur()} // avoid scroll changing value
                        required
                        className={`w-full max-w-md rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isSubmitted ? "bg-gray-100 cursor-not-allowed" : ""
                            }`}
                    />

                    {inputData.units && (
                        <div className="rounded-md bg-gray-100 border border-gray-300 px-3 py-2 text-sm text-gray-700">
                            {inputData.units}
                        </div>
                    )}
                </div>

               
                {isSubmitted && (
                    <div className="flex flex-col items-start mt-4 space-y-2">
                        {canGrade && (
                            <CorrectIndicator answeredCorrectly={answeredCorrectly} submitted={isSubmitted} />
                        )}

                        <p className="font-semibold text-green-700">
                            ✅ Correct Answer:{" "}
                            <span className="font-normal text-black">
                                {formatted.answerString ?? (canGrade ? String(correctNum) : "—")}
                            </span>
                        </p>

                        <p className="font-semibold text-blue-700">
                            📝 Your Answer:{" "}
                            <span className="font-normal text-black">
                                {submittedAnswer ?? "—"}
                            </span>
                        </p>
                    </div>
                )}
            </fieldset>
        </MathJax>
    );
}
