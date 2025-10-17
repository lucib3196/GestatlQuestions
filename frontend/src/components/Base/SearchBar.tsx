
import clsx from "clsx";

type SearchBarProps = {
    value: string;
    setValue: (val:string)=>void;
    disabled: boolean;
};
export default function SearchBar({ value, setValue, disabled }: SearchBarProps) {
    return (
        <input
            type="text"
            value={value}
            disabled={disabled}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Search questions by title..."
            className={clsx(
                "w-full rounded-md border px-4 py-2 transition",
                "focus:outline-none focus:ring-2 focus:ring-blue-500",
                "text-gray-900 dark:text-gray-200",
                // ✅ Conditional styling
                disabled
                    ? "bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600 cursor-not-allowed opacity-60"
                    : "bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 hover:border-blue-400"
            )}
        />
    );
}
