// --- Core React ---
import React from "react";

// --- API ---
import { saveFileContent } from "../../api";

import { SaveCodeButton } from "../Generic/Buttons";


// --- Props Interface ---
interface CodeEditorOptionsProps {
    selectedFile: string;
    fileContent: string;
    selectedQuestion: string | null;
}

// --- Component ---
export const CodeEditorOptions: React.FC<CodeEditorOptionsProps> = ({
    selectedFile,
    fileContent,
    selectedQuestion,
}) => {


    const saveCode = async () => {
        const qs = String(selectedQuestion ?? "").trim();
        await saveFileContent(selectedFile, fileContent, qs);
    };

    return (
        <div className="flex flex-row justify-start gap-x-5">
            <SaveCodeButton onClick={saveCode} />
            {/* <CreateFileButton onClick={() => setShowAddFile((prev) => !prev)} />
            <UploadFileButton onClick={() => setUploadFile((prev) => !prev)} /> */}

            {/* {showAddFile && <CreateFileModal showModal={setShowAddFile} />}
            {uploadFile && <UploadFileModal setShowModal={setUploadFile} />} */}
        </div>
    );
};
