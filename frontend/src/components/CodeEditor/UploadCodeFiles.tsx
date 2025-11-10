import { MyButton } from "../Base/Button";
import { useState } from "react";
import UploadFiles from "../Forms/UploadFileComponent";


export function UploadCodeFile({ questionId, onSubmit }: { questionId: string, onSubmit: (questionId: string, files: File[]) => void }) {
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const onFileSelect = (files: File[]) => {
        setUploadedFiles(files);
    };

    return (
        <div className="flex flex-col items-center w-full  mx-auto p-4">
            {/* Header */}
            <h1 className="text-lg sm:text-xl font-semibold tracking-wide text-black mb-4">
                Upload Files to Question
            </h1>

            {/* Upload Section */}
            <div className="w-full mb-4">
                <UploadFiles onFilesSelected={onFileSelect} />
            </div>

            {/* Uploaded Files List */}
            <div className="flex flex-col gap-1 w-full text-sm text-gray-800">
                {uploadedFiles.map((f, i) => (
                    <div
                        key={i}
                        className="border border-gray-200 rounded-md px-3 py-1 bg-gray-50 hover:bg-gray-100 transition-colors"
                    >
                        {f.name}
                    </div>
                ))}
            </div>

            <div>
                <MyButton name="Upload" onClick={() => onSubmit(questionId, uploadedFiles)} />
            </div>
        </div>
    );
}