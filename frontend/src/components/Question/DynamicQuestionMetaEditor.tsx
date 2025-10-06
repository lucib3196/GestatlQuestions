import type { Question } from "../../types/questionTypes";
import { MockData } from "./QuestionHeader";
import { FaPencil } from "react-icons/fa6";
import type { JSX } from "react";
import React, { useState } from "react";

type LabelMappingType = Record<Partial<keyof Question>, string>;
const labelMapping: LabelMappingType = {
    title: "Title",
    topics: "Topics",
    qtypes: "Question Type",
    isAdaptive: "Adaptive",
};

type Renderers<T> = Partial<{
    [K in keyof T]: (
        value: T[K],
        onChange: (v: T[K]) => void
    ) => JSX.Element | React.ReactNode;
}>;

const questionRenderer: Renderers<Question> = {
    title: (value, onChange) => (
        <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
        />
    ),
    topics: (value, onChange) => (
        <div>
            {value.map((v, i) => (
                <input
                    key={i}
                    type="text"
                    value={v}
                    onChange={(e) => {
                        const newTopics = [...value];
                        newTopics[i] = e.target.value;
                        onChange(newTopics);
                    }}
                />
            ))}
        </div>
    ),
    isAdaptive: (value, onChange) => (
        <input
            type="checkbox"
            checked={value}
            onChange={(e) => onChange(e.target.checked)}
        />
    ),
};

export function QuestionRendererContainer({ children }: React.ReactNode) {
    const [editMode, setEditMode] = useState(false);

    return (
        <div className="flex flex-col sm:flex-row gap-2 sm:items-baseline">
            <FaPencil
                className="cursor-pointer text-gray-600 hover:text-blue-600"
                onClick={() => setEditMode((prev) => !prev)}
            />
            {

            }
        </div>
    );
}

export default function UpdateQuestionMetaForm() {
    const [question, setQuestion] = useState<Question>(MockData);
    const validMetaFields: Array<keyof Question> = [
        "title",
        "topics",
        "qtypes",
        "isAdaptive",
    ];
    function updateField<K extends keyof Question>(key: K, value: Question[K]) {
        setQuestion((prev) => ({ ...prev, [key]: value }));
    }

    return (
        <div>
            FormData
            <form>
                {validMetaFields.map((key) => {
                    const renderer = questionRenderer[key];
                    if (!renderer) return null;
                    return (
                        <>
                            <label htmlFor={key} id={key}>
                                {key}
                            </label>
                            {renderer(question[key], (val) => updateField(key, val))}
                        </>
                    );
                })}
            </form>
        </div>
    );
}
