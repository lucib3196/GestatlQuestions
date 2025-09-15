type SubmitAnswerButtonProps = {
    onClick?: () => void;
    disabled?: boolean
};

export function SubmitAnswerButton({ onClick, disabled = false }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`inline-flex h-full items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
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

export function SaveCodeButton({ onClick, disabled }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled} className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed"
                    : "bg-indigo-500 text-white border-indigo-500 hover:bg-indigo-700 hover:text-white hover:border-primary-blue focus:ring-primary-blue"
                }`}
        >
            Save Code
        </button>
    )
}

export function CreateFileButton({ onClick, disabled }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled} className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed"
                    : "bg-primary-blue text-white border-primary-blue hover:bg-accent-sky hover:text-black hover:border-accent-sky focus:ring-accent-sky"
                }`}
        >
            Create <br />File
        </button>
    )
}


export function UploadFileButton({ onClick, disabled }: SubmitAnswerButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-200 text-gray-400 border-gray-200 cursor-not-allowed"
                    : "bg-green-600 text-white border-green-600 hover:bg-green-700 hover:text-white hover:border-green-700 focus:ring-green-400"
                }`}
        >
            Upload <br />File
        </button>
    )
}


type ShowSolutionButtonProps = {
    onClick: () => void;
    disabled: boolean,
    showSolution: boolean
};

export function ShowSolutionStep({ onClick, disabled, showSolution }: ShowSolutionButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`inline-flex items-center justify-center px-6 py-2 rounded-lg font-semibold border shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
        ${disabled
                    ? "bg-gray-200 text-gray-400 border-gray-200 cursor-not-allowed"
                    : "bg-green-600 text-white border-green-600 hover:bg-green-700 hover:text-white hover:border-green-700 focus:ring-green-400"
                }`}
        >

            {!showSolution ? <div>Show  <br></br> Solution </div> : <div>Hide Solution</div>}

        </button>
    )
}

import clsx from "clsx"
type ButtonVariant = "primary" | "secondary" | "danger" | "success";
const variantClasses: Record<ButtonVariant, string> = {
    primary: "bg-indigo-500 text-white hover:bg-indigo-800",
    secondary: "bg-red-400 text-black hover:bg-red-500",
    danger: "bg-red-500 text-white hover:bg-red-600",
    success: "bg-green-500 text-white hover:bg-green-600",
};
type MyButtonProps = {
    name: string;
    variant?: ButtonVariant;
    className?: string;
    onClick?: () => void;
    disabled?: boolean;
    btype?: "button" | "submit" | "reset";
};

export const MyButton = ({ name, variant = "primary", className, onClick, disabled, btype = "button" }: MyButtonProps) => {
    return (
        <button
            type={btype}
            onClick={onClick}
            disabled={disabled}
            className={clsx(
                "px-4 py-2 rounded font-semibold transition-colors duration-300 ease-in-out hover:-translate-y-1 hover:scale-110",
                variantClasses[variant],
                disabled && "opacity-50 cursor-not-allowed",
                className
            )}
        >
            {name}
        </button>
    )
}
