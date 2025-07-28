
import React from "react";
import ModGenerators from "./BaseTemplate";
import api from "../../api";
import { useState } from "react";





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
    questions: string[];
    package_name: string;
};

const InputForm: React.FC = () => {
    const [formData, setFormData] = useState<QuestionData>({
        questions: [],
        package_name: "",
    });
    const [loading, setLoading] = useState<boolean>(false);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleQuestionChange = (
        e: React.ChangeEvent<HTMLTextAreaElement>, index: number
    ) => {
        const updatedQuestions = [...formData.questions];
        updatedQuestions[index] = e.target.value;
        setFormData({ ...formData, questions: updatedQuestions });
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await api.post("/codegen_v3/text", formData);
            console.log(response.data);
            // You may want to show a success alert here
        } catch (error) {
            console.log("Error Submitting Form", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto mt-8">
            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <span className="text-blue-600 font-semibold animate-pulse">Loading...</span>
                </div>
            ) : (
                <form
                    onSubmit={handleSubmit}
                    className="bg-white shadow-md rounded-lg px-8 pt-6 pb-8 mb-4 border border-gray-200"
                >
                    <div className="mb-6">
                        <label
                            htmlFor="package_name"
                            className="block text-gray-700 text-sm font-bold mb-2"
                        >
                            Folder Name
                        </label>
                        <input
                            type="text"
                            name="package_name"
                            id="package_name"
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-400"
                            value={formData.package_name}
                            onChange={handleChange}
                            placeholder="Folder Name"
                            required
                        />
                    </div>

                    <div className="mb-6">
                        <label
                            htmlFor="questionTextArea"
                            className="block text-gray-700 text-sm font-bold mb-2"
                        >
                            Enter Question
                        </label>
                        <textarea
                            name="question"
                            id="questionTextArea"
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-400 min-h-[100px]"
                            value={formData.questions[0] || ""}
                            onChange={(e) => handleQuestionChange(e, 0)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
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
