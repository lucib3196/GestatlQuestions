import React from "react";
import ModGenerators from "./BaseTemplate";
import PopUpHelp from "../PopUpHelp";
import api from "../../api";
import { toast } from 'react-toastify';
import { useState} from "react";

// Examples for the input container
const examples = [
    {
        name: "Projectile Motion",
        text: "A ball is thrown horizontally from the top of a 50-meter high building with an initial speed of 15 meters per second. Assuming there is no air resistance, calculate the time it takes for the ball to reach the ground.",
    },
    {
        name: "Spring Oscillation",
        text: "A mass-spring system oscillates with a period of 2 seconds. If the spring constant is 100 N/m, calculate the mass attached to the spring. Assume the motion is simple harmonic.",
    },
    {
        name: "Pressure Calculation",
        text: "A force of 200 Newtons is applied perpendicular to a circular cross-sectional area with a radius of 0.1 meters. Calculate the pressure exerted on the area.",
    },
];

type QuestionData = {
    question: string[];
    question_title: string;
};
const InputForm: React.FC = () => {
    // Wether the title is going to be ai generated
    const [isDefault, setIsDefault] = useState(false)
    const [formData, setFormData] = useState<QuestionData>({
        question: [],
        question_title: "",
    });

    // Generic for loading and and other utilities
    const [loading, setLoading] = useState<boolean>(false);



    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };
    const handleQuestionChange = (
        e: React.ChangeEvent<HTMLTextAreaElement>,
        index: number
    ) => {
        const updatedQuestions = [...formData.question];
        updatedQuestions[index] = e.target.value;
        setFormData({ ...formData, question: updatedQuestions });
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        // Get access token must be logged in to use the generator
        try {
            const token = localStorage.getItem("access_token");
            if (!token) {
                toast.error("Error: Must Be Logged In")
                return;
            }
            const res = await api.post(
                "/codegenerator/v4/text_gen",   // make sure this matches your FastAPI route
                formData,                       // send JSON if your backend expects JSON
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                }
            );
            toast.success("Generated Succesfully")
        } catch (error) {
            toast.error(`Unexpected Error ${error}`)
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-xl mx-auto mt-8">

            {loading ? (
                <div className="flex items-center justify-center py-12">
                    <span className="text-blue-600 font-semibold animate-pulse">Loading…</span>
                </div>
            ) : (
                <form
                    onSubmit={handleSubmit}
                    className="bg-white border border-gray-200 shadow-sm rounded-lg p-6 space-y-6"
                >
                    {/* Folder Name */}
                    <div className="space-y-2">
                        <label htmlFor="question_title" className="block text-sm font-semibold text-gray-800">
                            Folder Name
                        </label>

                        <div className="flex items-start gap-3">
                            <input
                                type="text"
                                name="question_title"
                                id="question_title"
                                className={`flex-1 shadow-sm border rounded-md w-full px-3 py-2 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 ${isDefault ? "bg-gray-200" : ""}`}
                                value={formData.question_title}
                                onChange={handleChange}
                                placeholder="Enter a folder name"
                                disabled={isDefault}
                                required={!isDefault}
                                aria-describedby="package_help"
                            />

                            <div className="flex items-center gap-2">
                                <input
                                    id="use_default_title"
                                    type="checkbox"
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    checked={isDefault}
                                    onChange={() => setIsDefault((prev) => !prev)}
                                />
                                <label htmlFor="use_default_title" className="text-sm text-gray-800 select-none">
                                    Use AI-generated title
                                </label>
                                <PopUpHelp message="Let the system generate a clear, concise folder name for you." />
                            </div>
                        </div>

                        <p id="package_help" className="text-xs text-gray-500">
                            Choose a name to save the question (defaults to AI generated if checked).
                        </p>


                    </div>

                    {/* Question */}
                    <div className="space-y-2">
                        <label
                            htmlFor="questionTextArea"
                            className="flex items-center gap-2 text-sm font-semibold text-gray-800"
                        >
                            Enter Question
                            <PopUpHelp message="Works best with one question at a time (numerical or multiple choice)." />
                        </label>
                        <textarea
                            name="question"
                            id="questionTextArea"
                            className="shadow-sm border rounded-md w-full px-3 py-2 min-h-[110px] text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={formData.question[0] || ""}
                            onChange={(e) => handleQuestionChange(e, 0)}
                            placeholder="Type your question here…"
                            required
                        />
                    </div>

                    {/* Submit */}
                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    >
                        Submit
                    </button>
                </form>
            )}
        </div>

    );
};

export default function TextGenerator() {
    return (
        <>
            <ModGenerators
                title="Text Generator"
                subtitle="Creates dynamic educational modules based on input"
                examples={examples}
                inputComponent={<InputForm />}
            />
        </>
    );
}
