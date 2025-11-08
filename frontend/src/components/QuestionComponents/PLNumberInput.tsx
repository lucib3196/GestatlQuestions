import React, { useState } from "react";
import { MathJax } from "better-react-mathjax";

export type PLNumberInputProps = {
    answerName: string;
    comparison: string;
    digits: number | string;
    label: string | number;
    value: number | string;
    className?: string;
    variant?: keyof typeof variantStyles;
    onChange: (name: string, value: string) => void;
};


const variantStyles: Record<string, string> = {
    default: "border-gray-300 shadow-sm",
    minimal: "border-transparent bg-gray-50 hover:bg-gray-100",
};

const PLNumberInput: React.FC<PLNumberInputProps> = ({
    answerName,
    className = "",
    digits,
    label,
    value,
    variant = "default", // 👈 default variant
    onChange,
}) => {
    const step = 1 / Math.pow(10, Number(digits) || 0);

    return (
        <MathJax>
            <div className={className}>
                <fieldset
                    className={`border rounded-lg p-4 mb-4 ${variantStyles[variant]} ${className}`}
                >
                    <label
                        htmlFor={answerName}
                        className="text-sm font-bold text-gray-700 px-2"
                    >
                        {label}
                    </label>
                    <input
                        id={answerName}
                        name={answerName}
                        type="number"
                        step={step}
                        placeholder={String(answerName)}
                        value={value}
                        onChange={(e) => onChange(answerName, e.target.value)}
                        className="w-full max-w-md rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                </fieldset>
            </div>
        </MathJax>
    );
};

export default PLNumberInput