import React from "react";
import clsx from "clsx";

export type PLQuestionPanelSize = "sm" | "md" | "lg";
export type PLQuestionPanelVariant = "default" | "minimal";

export interface PLQuestionPanelProps {
    children?: React.ReactNode;
    className?: string;
    size?: PLQuestionPanelSize | string;
    variant?: PLQuestionPanelVariant | string;
}

const variantStyles: Record<PLQuestionPanelVariant, string> = {
    default: "border border-gray-300 shadow-sm bg-white",
    minimal: "border border-gray-200 bg-gray-50 hover:bg-gray-100",
};

const sizeStyles: Record<PLQuestionPanelSize, string> = {
    sm: "p-2 min-w-[200px] min-h-[200px] md:min-w-[250px] md:min-h-[250px]",
    md: "p-4 min-w-[300px] min-h-[400px] md:min-w-[350px] md:min-h-[450px]",
    lg: "p-6 min-w-[400px] min-h-[500px] md:min-w-[500px] md:min-h-[600px]",
};

const PLQuestionPanel: React.FC<PLQuestionPanelProps> = ({
    children,
    className = "",
    size = "md",
    variant = "default",
}) => (
    <div
        className={clsx(
            "flex flex-col items-center text-center rounded-md transition-all duration-200",
            variantStyles[variant as PLQuestionPanelVariant],
            sizeStyles[size as PLQuestionPanelSize],
            className
        )}
    >
        {children}
    </div>
);

export default PLQuestionPanel;
