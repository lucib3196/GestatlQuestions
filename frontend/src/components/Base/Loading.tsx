import { FaGear } from "react-icons/fa6";

export const Loading = () => {
    return (
        <div className="flex flex-col items-center justify-center w-full max-w-5xl mx-auto my-12 px-4">
            {/* Icon animation */}
            <FaGear className="animate-spin text-4xl text-gray-600 dark:text-gray-300 mb-4" />

            {/* Loading text */}
            <p className="text-base font-medium text-gray-700 dark:text-gray-300">
                Loading ...
            </p>

            {/* Skeleton blocks */}

        </div>
    );
};
