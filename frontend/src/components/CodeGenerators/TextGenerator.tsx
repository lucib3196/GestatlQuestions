import React, { useCallback, useEffect, useState } from "react";
import ModGenerators from "./BaseTemplate";
import { PopUpHelpIcon } from "../Base/PopUpHelper";
import api from "../../api/client";
import { toast } from "react-toastify";
import { AddQuestionInput } from "./AddQuestionInput";

// Examples for the input container
const examples = [
    {
        name: "Projectile Motion",
        text:
            "A ball is thrown horizontally from the top of a 50-meter high building with an initial speed of 15 meters per second. Assuming there is no air resistance, calculate the time it takes for the ball to reach the ground.",
    },
    {
        name: "Spring Oscillation",
        text:
            "A mass-spring system oscillates with a period of 2 seconds. If the spring constant is 100 N/m, calculate the mass attached to the spring. Assume the motion is simple harmonic.",
    },
    {
        name: "Pressure Calculation",
        text:
            "A force of 200 Newtons is applied perpendicular to a circular cross-sectional area with a radius of 0.1 meters. Calculate the pressure exerted on the area.",
    },
];

type QuestionData = {
    question: string;
    question_title?: string;
};

type QuestionInputProps = {
    i: number;
    formData: QuestionData[];
    setFormData: React.Dispatch<React.SetStateAction<QuestionData[]>>;
};

const QuestionInput: React.FC<QuestionInputProps> = ({ i, formData, setFormData }) => {
    const [isDefault, setIsDefault] = useState(false);
    const item = formData[i] ?? ({} as QuestionData);

    const handleChange = useCallback(
        (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
            const { name, value } = e.target;
            setFormData((prev) => {
                const next = [...prev];
                const current = next[i] ?? ({} as QuestionData);
                next[i] = { ...current, [name]: value };
                return next;
            });
        },
        [i, setFormData]
    );

    return (
        <div className="space-y-4">
            {/* Folder Name */}
            <div className="space-y-2">
                <label htmlFor={`question_title_${i}`} className="block text-sm font-semibold text-gray-800">
                    Folder Name
                </label>

                <div className="flex items-start gap-3">
                    <input
                        type="text"
                        name="question_title"
                        id={`question_title_${i}`}
                        className={`flex-1 w-full rounded-md border px-3 py-2 text-gray-900 placeholder:text-gray-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${isDefault ? "bg-gray-200" : ""
                            }`}
                        value={item.question_title ?? ""}
                        onChange={handleChange}
                        placeholder="Enter a folder name"
                        disabled={isDefault}
                        required={!isDefault}
                        aria-describedby={`question_title_help_${i}`}
                    />

                    <div className="flex items-center gap-2">
                        <input
                            id={`use_default_title_${i}`}
                            type="checkbox"
                            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            checked={isDefault}
                            onChange={() => setIsDefault((prev) => !prev)}
                        />
                        <label htmlFor={`use_default_title_${i}`} className="select-none text-sm text-gray-800">
                            Use AI-generated title
                        </label>
                        {/* <PopUpHelp message="Let the system generate a clear, concise folder name for you." /> */}
                    </div>
                </div>

                <p id={`question_title_help_${i}`} className="sr-only">
                    Provide a descriptive folder name or check the box to use an AI-generated title.
                </p>
            </div>

            {/* Question */}
            <div className="space-y-2">
                <label
                    htmlFor={`questionTextArea_${i}`}
                    className="flex items-center gap-2 text-sm font-semibold text-gray-800"
                >
                    Enter Question
                    <PopUpHelpIcon value="Works best with one question at a time (numerical or multiple choice)." />
                </label>
                <textarea
                    name="question"
                    id={`questionTextArea_${i}`}
                    className="min-h-[110px] w-full rounded-md border px-3 py-2 text-gray-900 placeholder:text-gray-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={item.question ?? ""}
                    onChange={handleChange}
                    placeholder="Type your question here…"
                    required
                />
            </div>
        </div>
    );
};

const InputForm: React.FC = () => {
    const [count, setCount] = useState(1);
    const handleCountChange = useCallback((next: number) => setCount(next), []);

    const [formData, setFormData] = useState<QuestionData[]>([{ question: "", question_title: "" }]);
    const [loading, setLoading] = useState<boolean>(false);

    // Keep formData length in sync with count
    useEffect(() => {
        setFormData((prev) => {
            if (prev.length === count) return prev;
            if (prev.length < count) {
                const add = Array.from({ length: count - prev.length }, () => ({ question: "", question_title: "" }));
                return [...prev, ...add];
            }
            return prev.slice(0, count);
        });
    }, [count]);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        try {
            


            const payload = formData.map(({ question, question_title }) => ({
                question,
                ...(question_title?.trim() ? { question_title } : {}),
            }));



            const requests = payload.map((dataItem) =>
                api.post(
                    "/codegenerator/v5/text_gen",
                    { data: dataItem },
                )
            );
            const responses = await Promise.all(requests);
            console.log(responses)

            toast.success("Generated successfully");
        } catch (error: any) {
            const msg = error?.response?.data?.detail ?? error?.message ?? "Unexpected error";
            toast.error(String(msg));
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <span className="animate-pulse font-semibold text-blue-600">Loading…</span>
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-full px-4 py-8">
            {/* Header / controls */}
            <div className="mb-4 flex items-center justify-between">
                <h1 className="text-xl font-semibold text-gray-900">Create Questions</h1>
                <div className="flex items-center gap-3">
                    <span className="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700">
                        {count} {count === 1 ? "question" : "questions"}
                    </span>
                    <AddQuestionInput value={count} onChange={handleCountChange} />
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
                {/* Question cards */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                    {Array.from({ length: count }, (_, i) => (
                        <div
                            key={i}
                            className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm ring-1 ring-black/5 transition hover:shadow-md"
                        >
                            <div className="mb-3 flex items-center justify-between">
                                <span className="text-sm font-medium text-gray-600">Question {i + 1}</span>
                                <span className="rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700">#{i + 1}</span>
                            </div>

                            <QuestionInput i={i} formData={formData} setFormData={setFormData} />
                        </div>
                    ))}
                </div>

                {/* Submit */}
                <div className="pt-2">
                    <button
                        type="submit"
                        className="inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm ring-1 ring-indigo-500/30 transition hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        Submit
                    </button>
                </div>
            </form>
        </div>
    );
};

export default function TextGenerator() {
    return (
        <ModGenerators
            title="Text Generator"
            subtitle="Creates dynamic educational modules based on input"
            examples={examples}
            inputComponent={<InputForm />}
        />
    );
}
