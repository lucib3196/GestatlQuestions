import { MdDriveFolderUpload } from "react-icons/md";

type UploadFilesProp = {
    onFilesSelected: (files: File[]) => void;
};

export default function UploadFiles({ onFilesSelected }: UploadFilesProp) {
    const handleClick = () => {
        document.getElementById("file-input")?.click();
    };

    return (
        <div
            className="
        w-full max-w-md mx-auto cursor-pointer rounded-lg border-2 border-dashed 
        border-blue-400 bg-blue-50 dark:bg-gray-800 dark:border-blue-600 
        hover:bg-blue-100 dark:hover:bg-gray-700 
        focus-within:outline-none focus-within:ring-2 focus-within:ring-blue-500
        transition-colors p-8 flex flex-col items-center justify-center text-center
      "
            onClick={handleClick}
            role="button"
            tabIndex={0}
        >
            <MdDriveFolderUpload
                className="text-blue-500 dark:text-blue-400 mb-3"
                size={40}
            />
            <span className="text-lg font-semibold text-blue-700 dark:text-blue-300">
                Click to select file(s)
            </span>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Supports multiple files (HTML, JS, PY)
            </p>

            <input
                type="file"
                id="file-input"
                className="sr-only"
                multiple
                onChange={(e) => {
                    const files = e.target.files ? Array.from(e.target.files) : [];
                    onFilesSelected(files);
                }}
            />
        </div>
    );
}
