
type SolutionPanelProps = {
    solution: string[]
}

export function SolutionPanel({ solution }: SolutionPanelProps) {
    if (!solution || solution.length === 0) return null;

    return (
        <div className="flex flex-col items-center rounded-2xl max-w-[90%] shadow-lg p-10 px-8 my-10 text-center bg-white border border-gray-200 hover:shadow-xl transition-shadow duration-200">
            <ol className="list-decimal list-inside space-y-4 text-left w-full max-w-3xl">
                {solution.map((value, idx) => (
                    <li key={idx} className="text-lg text-gray-800 whitespace-pre-line">
                        {value}
                    </li>
                ))}
            </ol>
        </div>
    );
}
