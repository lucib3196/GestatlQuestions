import type { QuestionMetadata } from "../../types/types";
import Pill from "../Pill";
export default function QuestionInfo({ qmetadata }: { qmetadata: QuestionMetadata }) {
    console.log("This is the qdata", qmetadata)
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