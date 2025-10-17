export const SimpleToggle = ({
    setToggle,
    label,
    id,
    checked = false
}: {
    setToggle: () => void;
    label: string;
    id: string;
    checked?: boolean
}) => (
    <label
        htmlFor={id}
        onClick={setToggle}
        className="flex items-center gap-2 cursor-pointer select-none text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors duration-150 hover:text-blue-600 dark:hover:text-blue-400"
    >
        <input
            type="checkbox"
            id={id}
            name={id}
            checked={checked}
            className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 dark:focus:ring-offset-gray-800"
        />
        <span onClick={setToggle}>{label}</span>
    </label>
);