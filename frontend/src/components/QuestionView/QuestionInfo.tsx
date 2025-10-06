import type { QuestionMeta } from "../../types/types";
import { Pill, PillContainer } from "../Base/Pill";


type GenericInfoProps = {
    title: string;
    data: string[]
}
const GenericInfo = ({ title, data }: GenericInfoProps) => {
    return (
        <div className="flex flex-row items-start gap-x-4">
            <p className="min-w-[150px] text-lg font-bold text-gray-700">{title}</p>
            <div className="flex flex-wrap gap-x-2 gap-y-5">
                {(data ?? []).map((val, id) => (
                    <Pill
                        key={id}
                    >{val}</Pill>
                ))}
            </div>
        </div>
    )
}

export default function QuestionInfo({ qmetadata }: { qmetadata: QuestionMeta }) {
    const { title, topics, isAdaptive } = qmetadata;

    return (
        <div className="flex flex-col w-full max-w-3xl p-4 rounded-md  bg-white space-y-3">
            <h2 className="text-xl text-center font-bold text-gray-800">{title}</h2>

            <div className="flex flex-col gap-4">

                {/* Topics Section */}
                <GenericInfo title={"Topics"} data={(topics ?? []).map(t => t.name)} />

                <div className="flex flex-row items-center gap-x-4">
                    <p className="min-w-[150px] text-lg font-bold text-gray-700">Adaptive:</p>
                    <span
                        className={`px-3 py-1 rounded-full text-sm font-medium 
                            ${isAdaptive === true
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