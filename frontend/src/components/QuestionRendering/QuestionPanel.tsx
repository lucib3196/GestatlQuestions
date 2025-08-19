
import type { QuestionMetadata } from "../../types/types";




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

