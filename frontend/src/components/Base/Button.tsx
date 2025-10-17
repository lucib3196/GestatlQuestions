import clsx from "clsx";


type ButtonColor =
  | "primary"
  | "secondary"
  | "danger"
  | "success"
  | "warning"
  | "neutral"
  | "submitQuestion"
  | "generateVariant"
  | "showSolution";

const colorClasses: Record<ButtonColor, string> = {
  primary:
    "bg-indigo-500 text-white hover:bg-indigo-600 dark:bg-indigo-700 dark:hover:bg-indigo-800",
  secondary:
    "bg-gray-300 text-gray-900 hover:bg-gray-400 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600",
  danger:
    "bg-red-500 text-white hover:bg-red-600 dark:bg-red-700 dark:hover:bg-red-800",
  success:
    "bg-green-500 text-white hover:bg-green-600 dark:bg-green-700 dark:hover:bg-green-800",
  warning:
    "bg-yellow-400 text-black hover:bg-yellow-500 dark:bg-yellow-600 dark:hover:bg-yellow-700",
  neutral:
    "bg-transparent border border-gray-400 text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-800",

  // 🟦 Submit Question
  submitQuestion:
    "bg-blue-500 text-white hover:bg-blue-600 dark:bg-blue-700 dark:hover:bg-blue-800",

  // 🟣 Generate New Variant
  generateVariant:
    "bg-purple-500 text-white hover:bg-purple-600 dark:bg-purple-700 dark:hover:bg-purple-800",

  // 🟩 Show Solution
  showSolution:
    "bg-cyan-500 text-white hover:bg-cyan-600 dark:bg-cyan-700 dark:hover:bg-cyan-800",
};


type ButtonSize = "sm" | "md" | "lg";

const sizeClasses: Record<ButtonSize, string> = {
    sm: "px-2 py-1 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
};


type MyButtonProps = {
    name: string;
    color?: ButtonColor;
    size?: ButtonSize;
    className?: string;
    onClick?: (() => void) | ((e: React.MouseEvent<HTMLButtonElement>) => void);
    disabled?: boolean;
    btype?: "button" | "submit" | "reset";
};


export const MyButton = ({
    name,
    color = "primary",
    size = "md",
    className,
    onClick,
    disabled,
    btype = "button",
}: MyButtonProps) => {
    return (
        <button
            type={btype}
            onClick={onClick}
            disabled={disabled}
            className={clsx(
                "rounded font-semibold transition-all duration-300 ease-in-out transform hover:-translate-y-0.5 hover:scale-105",
                colorClasses[color],
                sizeClasses[size],
                disabled && "opacity-50 cursor-not-allowed",
                className
            )}
        >
            {name}
        </button>
    );
};
