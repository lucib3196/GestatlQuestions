// src/features/questions/TableToolbar.tsx
import { TableToolBarButton } from "../QuestionTable/TableToolBarButtons";
import { useState } from "react";
import { FiUpload } from "react-icons/fi";
import CreateQuestion from "../CreateQuestion/CreateQuestion";
import { MdDriveFolderUpload } from "react-icons/md";

export const UploadQuestion: React.FC = () => {
    const handleClick = () => {
        const data = document.getElementById('file-input')?.click();
        console.log("This is the data", data)
    };

    return (
        <div className="w-full h-full flex flex-col items-center px-4 py-8">
            <h1 className="text-2xl font-semibold text-center mb-2">
                Upload a ZIP of Your Questions
            </h1>
            <p className="text-center text-gray-600 mb-6">
                Please make sure it includes at least a <code className="font-mono bg-gray-100 px-1 rounded">question.html</code> file.
            </p>

            <div
                className="w-full max-w-md cursor-pointer rounded-lg border-2 border-dashed border-blue-400 bg-blue-50 hover:bg-blue-100 focus-within:outline-none focus-within:ring-2 focus-within:ring-blue-500 transition-colors p-6 flex flex-col items-center"
                onClick={handleClick}
                role="button"
                tabIndex={0}
                onKeyPress={(e) => e.key === 'Enter' && handleClick()}
            >
                <MdDriveFolderUpload className="text-blue-500 mb-2" size={32} />
                <span className="text-lg font-medium text-blue-700">
                    Click to select a ZIP file
                </span>
                <input
                    type="file"
                    id="file-input"
                    accept=".zip"
                    className="sr-only"
                    onChange={(e) => {
                        const file = e.target.files?.[0];
                        console.log('Selected file:', file);
                    }}
                />
            </div>
        </div>
    );
};




export const UploadQuestionButton = () => {
    const [_, setShowPopUp] = useState(false)
    return (
        <>
            <TableToolBarButton
                value="Upload Question"
                className="border-indigo-600 text-indigo-700 hover:bg-indigo-200 "
                onClick={() => setShowPopUp(prev => !prev)}
                icon={<FiUpload className="self-center" />}
            />
            {
                <CreateQuestion />
            }
        </>
    );
};