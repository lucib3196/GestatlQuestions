import clsx from "clsx";
import { API_URL } from "../../config";
import { useQuestionContext } from "../../context/QuestionContext";

export type ImageSize = "sm" | "md" | "lg";

export interface PLFigureProps {
    src: string;
    className?: string;
    size?: ImageSize | string;
    variant?: "default" | "minimal" | string;
}

const variantStyles: Record<string, string> = {
    default: "border border-gray-300 shadow-sm rounded-lg bg-white",
    minimal: "border-transparent bg-gray-50 hover:bg-gray-100 rounded-lg",
};

const sizeStyles: Record<ImageSize, string> = {
    sm: "max-w-[150px] md:max-w-[200px]",
    md: "max-w-[300px] md:max-w-[400px]",
    lg: "max-w-[500px] md:max-w-[700px]",
};

export default function PLFigure({
    src,
    className = "",
    size = "md",
    variant = "default",
}: PLFigureProps) {
    const { questionMeta: qdata } = useQuestionContext();

    const imagePath = `${API_URL}/${qdata?.question_path}/clientFiles/${src}`;

    return (
        <div
            className={clsx(
                "flex justify-center items-center overflow-hidden my-4",
                variantStyles[variant],
                className
            )}
        >
            <img
                src={imagePath}
                alt={src}
                className={clsx(
                    "w-full h-auto object-contain transition-transform duration-200 hover:scale-[1.02]",
                    sizeStyles[size as ImageSize]
                )}
            />
        </div>
    );
}
