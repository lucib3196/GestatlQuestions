import clsx from "clsx";

export type PillTheme = "primary" | "secondary" | "success" | "danger" | "warning" | "info" | "purple" | "outline" | "minimal";

const PillStyle: Record<PillTheme, string> = {
    primary:
        "bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 dark:text-white",

    secondary:
        "bg-gray-200 text-gray-800 hover:bg-gray-300 border border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 dark:border-gray-600",

    success:
        "bg-green-100 text-green-800 hover:bg-green-200 border border-green-300 dark:bg-green-700 dark:text-green-100 dark:hover:bg-green-600 dark:border-green-600",

    danger:
        "bg-red-100 text-red-800 hover:bg-red-200 border border-red-300 dark:bg-red-700 dark:text-red-100 dark:hover:bg-red-600 dark:border-red-600",

    warning:
        "bg-yellow-100 text-yellow-900 hover:bg-yellow-200 border border-yellow-300 dark:bg-yellow-700 dark:text-yellow-100 dark:hover:bg-yellow-600 dark:border-yellow-600",

    info:
        "bg-sky-100 text-sky-800 hover:bg-sky-200 border border-sky-300 dark:bg-sky-700 dark:text-sky-100 dark:hover:bg-sky-600 dark:border-sky-600",

    purple:
        "bg-purple-100 text-purple-800 hover:bg-purple-200 border border-purple-300 dark:bg-purple-700 dark:text-purple-100 dark:hover:bg-purple-600 dark:border-purple-600",

    outline:
        "border border-gray-400 text-gray-700 hover:bg-gray-100 dark:border-gray-500 dark:text-gray-200 dark:hover:bg-gray-800",

    minimal:
        "bg-transparent text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white",
};



type PillProps = {
    children: React.ReactNode;
    theme?: PillTheme;
};
type PillContainerProps = {
    children: React.ReactNode
}

export const Pill: React.FC<PillProps> = ({ children, theme = "primary" }) => {
    return (
        <div
            className={clsx(
                "flex items-center truncate",
                // Responsive sizing
                "px-2 py-0.5 text-xs",
                "sm:px-3 sm:py-1 sm:text-sm",
                "md:px-4 md:py-1.5 md:text-base",
                // Shape + styling
                "rounded-full font-medium shadow-sm transition-colors cursor-default",
                "max-w-[6rem] sm:max-w-xs md:max-w-md",
                PillStyle[theme]
            )}
        >
            {children}
        </div>
    );
};

export const PillContainer: React.FC<PillContainerProps> = ({ children }) => {
    return (
        <div className="flex flex-wrap gap-2 sm:gap-3 md:gap-4">
            {children}
        </div>
    );
};
