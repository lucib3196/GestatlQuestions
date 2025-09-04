import React, { useMemo } from "react";
import { shuffleArray } from "../../utils/mathHelpers";
import Checkbox from "@mui/material/Checkbox";
import { useState, useEffect } from "react";
import type { MultipleChoiceOption } from "../../types/types";
import CorrectIndicator from "../Generic/CorrectIndicator";

type MultipleChoiceProps = {
    name: string;
    label: string;
    options: MultipleChoiceOption[];
    isSubmitted: boolean;
    shuffle: boolean;
};

export const MultipleChoiceInput: React.FC<MultipleChoiceProps> = ({
    label,
    options,
    shuffle,
    isSubmitted,
}) => {
    const [checkedArr, setCheckedArr] = useState<boolean[]>(
        options?.map(() => false) ?? []
    );
    const [submittedOptions, setSubmittedOptions] = useState<
        MultipleChoiceOption[]
    >([]);

    const answerChoices = useMemo(() => {
        if (!options) return [];
        const choices = options.map((el, id) => ({
            id,
            ...el,
        }));
        return shuffle ? shuffleArray(choices) : choices;
    }, [options, shuffle]);

    useEffect(() => {
        // Reset the question due to shuffle
        setCheckedArr(answerChoices.map(() => false));
        console.log("Resetting checked array:", checkedArr);
    }, [isSubmitted]);

    function handleChange(ind: number) {
        setCheckedArr((prev) => {
            const updated = prev.map((el, idx) => (idx === ind ? !el : el));
            console.log(`Toggled index ${ind}, new state:`, updated);
            return updated;
        });
    }

    function handleSubmit() {
        const selectedIndices = checkedArr
            .map((checked, index) => (checked ? index : -1))
            .filter((index) => index !== -1);

        const selectedOptions = selectedIndices.map((i) => answerChoices[i]);
        setSubmittedOptions(selectedOptions);
    }

    useEffect(() => {
        handleSubmit();
    }, [isSubmitted]);

    return (
        <div className="w-full border rounded-md px-2 py-3 mt-4 space-y-3">
            <div className="flex flex-row text-center justify-center mt-5">
                <p className="font-semibold">{label}</p>
            </div>
            {answerChoices.map((el, ind) => (
                <div
                    className="flex w-full items-center px-4 py-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                    key={el.id}
                >
                    <Checkbox
                        checked={!!checkedArr[ind]}
                        onChange={() => handleChange(ind)}
                    />
                    <div>{el.name}</div>
                </div>
            ))}
            {isSubmitted && (
                <div className="mt-4 space-y-3">
                    <p className="font-semibold text-blue-600">
                        📝 Your Selected Answers:
                    </p>
                    {submittedOptions.map((value, idx) => (
                        <div
                            key={idx}
                            className="flex  justify-start items-baseline text-center gap-x-4 bg-gray-100 px-4 py-2 rounded-md shadow-sm"
                        >
                            <p className="text-gray-800">• {value.name}</p>
                            <CorrectIndicator
                                answeredCorrectly={value.isCorrect}
                                submitted={isSubmitted}
                            />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
