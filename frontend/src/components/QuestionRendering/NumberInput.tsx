import { useState } from "react";
import { MathJax } from "better-react-mathjax";
import CorrectIndicator from "../CorrectIndicator";
import { isCloseEnoug } from "../../utils/mathHelpers";
import type { NumberInput } from "../../types/types";

type NumberInputProps = {
    inputData: NumberInput;
    correctAnswers: number;
    isSubmitted: boolean;
};

export function NumberInputDynamic({
    inputData,
    correctAnswers,
    isSubmitted,
}: NumberInputProps) {
    const name = inputData.name;
    const displayLabel = inputData.label || name;
    const [submittedAnswer, setSubmittedAnswer] = useState<number>();

    return (
        <MathJax>
            <fieldset className="border border-gray-300 rounded-lg p-4 mb-4 shadow-sm">
                <legend className="text-sm font-bold text-gray-700 px-2">Answer</legend>

                {/* Input Row */}
                <div className="flex flex-row flex-wrap items-center gap-2">
                    <label htmlFor={name} className="text-sm font-medium text-gray-600">
                        {displayLabel}
                    </label>

                    <input
                        type="number"
                        name={name}
                        id={name}
                        size={50}
                        disabled={isSubmitted}
                        onChange={(e) => setSubmittedAnswer(Number(e.target.value))}
                        required
                        className={`w-full max-w-md rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isSubmitted ? "bg-gray-400" : ""
                        }`}
                    />

                    {inputData.units && (
                        <div className="rounded-md bg-gray-200 border border-gray-300 px-3 py-2">
                            {inputData.units}
                        </div>
                    )}
                </div>

                {/* Submission Feedback */}
                {isSubmitted && (
                    <div className="flex flex-col items-start mt-4 space-y-2">
                        <CorrectIndicator
                            answeredCorrectly={isCloseEnoug(correctAnswers, submittedAnswer as number)}
                            submitted={isSubmitted}
                        />

                        <p className="font-semibold text-green-700">
                            ✅ Correct Answer:{" "}
                            <span className="font-normal text-black">{correctAnswers}</span>
                        </p>

                        <p className="font-semibold text-blue-700">
                            📝 Your Answer:{" "}
                            <span className="font-normal text-black">{submittedAnswer}</span>
                        </p>
                    </div>
                )}
            </fieldset>
        </MathJax>
    );
}
