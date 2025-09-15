// --- Core React ---
import React, { useState } from "react";

// --- API ---
import { saveFileContent } from "../../api";

import CreateFileModal from "./CreateFileModal";
import { CreateFileButton, SaveCodeButton, UploadFileButton } from "../Generic/Buttons";
import { UploadFileModal } from "./UploadFileModal";


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
    const [showAddFile, setShowAddFile] = useState<boolean>(false);
    const [uploadFile, setUploadFile] = useState<boolean>(false);

    const saveCode = async () => {
        const qs = String(selectedQuestion ?? "").trim();
        await saveFileContent(selectedFile, fileContent, qs);
    };

    return (
        <div className="flex flex-row justify-start gap-x-5">
            <SaveCodeButton onClick={saveCode} />
            <CreateFileButton onClick={() => setShowAddFile((prev) => !prev)} />
            <UploadFileButton onClick={() => setUploadFile((prev) => !prev)} />

            {showAddFile && <CreateFileModal showModal={setShowAddFile} />}
            {uploadFile && <UploadFileModal setShowModal={setUploadFile} />}
        </div>
    );
};
