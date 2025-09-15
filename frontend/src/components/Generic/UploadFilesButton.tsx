import { MdDriveFolderUpload } from "react-icons/md";

type UploadFilesButtonProps = {
    onFilesSelected: (files: File[]) => void;
};

export default function UploadFilesButton({ onFilesSelected }: UploadFilesButtonProps) {
    const handleClick = () => {
        document.getElementById("file-input")?.click();
    };
    return (
        <div
            className="w-6/10 justify-self-center cursor-pointer rounded-lg border-2 border-dashed border-blue-400 bg-blue-50 hover:bg-blue-100 focus-within:outline-none focus-within:ring-2 focus-within:ring-blue-500 transition-colors p-6 flex flex-col items-center"
            onClick={handleClick}
            role="button"
            tabIndex={0}
        >
            <MdDriveFolderUpload className="text-blue-500 mb-2" size={32} />
            <span className="text-lg font-medium text-blue-700">
                Click to select file(s)
            </span>
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