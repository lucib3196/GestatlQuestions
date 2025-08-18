
import type { QuestionMetadata } from "../../types/types";

import Pill from "../Pill";


export function QuestionInfo({ qmetadata }: { qmetadata: QuestionMetadata }) {
    const { title, topic, relevantCourses, isAdaptive } = qmetadata;
    console.log("inside question info", title)

    return (
        <div className="flex flex-col w-full max-w-3xl p-4 rounded-md  bg-white space-y-3">
            <h2 className="text-xl text-center font-bold text-gray-800">{title}</h2>

            <div className="flex flex-col gap-4">

                {/* Topics Section */}
                <div className="flex flex-row items-start gap-x-4">
                    <p className="min-w-[150px] text-lg font-bold text-gray-700">Topics:</p>
                    <div className="flex flex-wrap gap-2">
                        {(topic ?? []).map((t, i) => (
                            <Pill key={i} content={t} />
                        ))}
                    </div>
                </div>

                {/* Relevant Courses Section */}
                <div className="flex flex-row items-start gap-x-4">
                    <p className="min-w-[150px] text-lg font-bold text-gray-700">Relevant Courses:</p>
                    <div className="flex flex-wrap gap-2">
                        {(relevantCourses ?? []).map((course, i) => (
                            <Pill
                                key={i}
                                content={course}
                                bgColor="bg-red-100"
                                textColor="text-red-800"
                            />
                        ))}
                    </div>
                </div>
                <div className="flex flex-row items-center gap-x-4">
                    <p className="min-w-[150px] text-lg font-bold text-gray-700">Adaptive:</p>
                    <span
                        className={`px-3 py-1 rounded-full text-sm font-medium 
                            ${isAdaptive === "True" || isAdaptive === true
                                ? "bg-green-100 text-green-700"
                                : "bg-red-100 text-red-700"
                            }`}
                    >
                        {String(isAdaptive)}
                    </span>
                </div>

            </div>


        </div>
    );
}
type QuestionPanelProps = {
    question: string;
    image?: string;
};
import { MathJax } from "better-react-mathjax";
export function QuestionPanel({ question, image }: QuestionPanelProps) {
    if (!question) return null;

    return (
    
            <div className="flex flex-col items-center rounded-2xl max-w-9/10 shadow-lg p-10 px-8 my-10 text-center bg-white border border-gray-200 hover:shadow-xl transition-shadow duration-200 space-y-6">
                {/* Question Text */}
                <p className="text-lg text-gray-800 whitespace-pre-line"><MathJax>{question}</MathJax></p>

                {/* Optional Image */}
                {image && (
                    <div className="w-full flex justify-center">
                        <div className="max-w-xl w-full rounded-lg overflow-hidden shadow-sm border border-gray-300">
                            <img
                                src={`http://localhost:8000/local_questions/${image}`}
                                alt="Question diagram"
                                className="w-full object-contain rounded-lg"
                            />

                        </div>
                    </div>
                )}
            </div>
        


    );
}

