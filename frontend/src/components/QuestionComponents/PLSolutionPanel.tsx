import React, { useState } from "react";
import clsx from "clsx";
import { MyButton } from "../Base/Button";
export type PLSolutionPanelSize = "sm" | "md" | "lg";
export type PLSolutionPanelVariant = "default" | "minimal";

export interface PLSolutionPanelProps {
    title?: string
    subtitle?: string
    /** Steps or solution content */
    children?: React.ReactNode;
    /** Additional styling */
    className?: string;
    /** Size of the panel */
    size?: PLSolutionPanelSize | string;
    /** Visual variant */
    variant?: PLSolutionPanelVariant | string;
    /** Whether to show all steps automatically */
    autoShowAll?: boolean;
}

const variantStyles: Record<PLSolutionPanelVariant, string> = {
    default: "border border-gray-300 shadow-sm bg-white",
    minimal: "border border-gray-200 bg-gray-50 hover:bg-gray-100",
};

const sizeStyles: Record<PLSolutionPanelSize, string> = {
    sm: "p-2 min-w-[200px] min-h-[200px] md:min-w-[250px] md:min-h-[250px]",
    md: "p-4 min-w-[300px] min-h-[400px] md:min-w-[350px] md:min-h-[450px]",
    lg: "p-6 min-w-[400px] min-h-[500px] md:min-w-[500px] md:min-h-[600px]",
};

const PLSolutionPanel: React.FC<PLSolutionPanelProps> = ({
    children,
    className = "",
    title="Solution",
    subtitle,
    size = "md",
    variant = "default",
    autoShowAll = false,
}) => {
    const [stepIndex, setStepIndex] = useState<number>(0);
    const steps = React.Children.toArray(children);
    const handleShowNext = () => {
        setStepIndex((prev) => Math.min(prev + 1, steps.length));
    };
    const handleReset = () => {
        setStepIndex(0)
    }

    const visibleSteps = autoShowAll ? steps : steps.slice(0, stepIndex);


    return (
        <div
            className={clsx(
                "h-full flex flex-col items-center text-center rounded-md transition-all duration-200 overflow-auto",
                variantStyles[variant as PLSolutionPanelVariant],
                sizeStyles[size as PLSolutionPanelSize],
                className
            )}
        >
            <div className="w-full overflow-auto">
                <h2 className="text-xl sm:text-2xl font-semibold">{title}</h2>
                {subtitle && (
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        {subtitle}
                    </p>
                )}
            </div>
            {/* Step content */}
            <div className="flex-1 w-full px-4 py-2">
                {visibleSteps}
            </div>

            {/* Buttons pinned to bottom */}
            <div className="mt-auto mb-4 flex justify-center gap-3">
                {!autoShowAll && stepIndex < steps.length - 1 ? (
                    <MyButton
                        name="Show Next Step"
                        onClick={handleShowNext}
                    />
                ) : (
                    <MyButton
                        name="Reset"
                        color="secondary"
                        onClick={handleReset}
                    />
                )}
            </div>

            <div className="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4 text-center text-xs text-gray-500 dark:text-gray-400">
                Review each step before proceeding.
            </div>
        </div>

    );
};

export default PLSolutionPanel;
