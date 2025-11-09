import React from "react";
import { MathJax } from "better-react-mathjax";
import clsx from "clsx";

export type PLHintVariant = "default" | "highlighted";

export interface PLHintProps {
    level: number | string;
    /** Hint content (supports Markdown or plain text rendered by parent) */
    children?: React.ReactNode;
    /** Visual style for the hint */
    variant?: PLHintVariant | string;
    /** Additional custom className */
    className?: string;
}

const variantStyles: Record<PLHintVariant, string> = {
    default:
        "border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50",
    highlighted:
        "border border-indigo-300 bg-indigo-50 dark:border-indigo-600/70 dark:bg-indigo-900/40",
};

export default function PLHint({
    level,
    children,
    variant = "default",
    className = "",
}: PLHintProps) {
    return (
        <MathJax>
            <div
                className={clsx(
                    "flex w-full items-start gap-4 rounded-lg p-4 mb-3 transition-all duration-200",
                    variantStyles[variant as PLHintVariant],
                    className
                )}
            >
                {/* Step indicator */}
                <div className="flex h-8 w-8 flex-none items-center justify-center rounded-full border border-indigo-300 bg-indigo-100 text-sm font-semibold text-indigo-700 dark:border-indigo-600 dark:bg-indigo-900 dark:text-indigo-100 shadow-sm">
                    {level}
                </div>

                {/* Hint content */}
                <div className="prose prose-indigo dark:prose-invert max-w-none text-left">
                    {children}
                </div>
            </div>
        </MathJax>
    );
}
