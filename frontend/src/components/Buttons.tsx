type SubmitAnswerButtonProps = {
    onClick: () => void;
    disabled: boolean
};

export function SubmitAnswerButton({ onClick, disabled = false }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed"
                    : "bg-primary-blue text-white border-primary-blue hover:bg-accent-sky hover:text-black hover:border-accent-sky focus:ring-accent-sky"
                }`}
        >
            Submit
        </button>
    );
}


export function ResetQuestionButton({ onClick, disabled }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled} className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed"
                    : "bg-accent-teal text-white border-accent-teal hover:bg-primary-blue hover:text-white hover:border-primary-blue focus:ring-primary-blue"
                }`}
        >
            Reset
        </button>
    )
}


export function GenerateNewVariantButton({ onClick, disabled }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled} className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed"
                    : "bg-indigo-500 text-white border-indigo-500 hover:bg-indigo-700 hover:text-white hover:border-primary-blue focus:ring-primary-blue"
                }`}
        >
            Generate <br />New Variant
        </button>
    )
}