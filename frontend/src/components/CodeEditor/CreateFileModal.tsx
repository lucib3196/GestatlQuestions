import { useState } from "react";
import { CloseButton } from "../CloseButton";
import api from "../../api";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";

import { useContext } from "react";



type CreateFileProps = {
    showModal: (visible: boolean) => void;
};


function CreateFileModal({ showModal }: CreateFileProps) {
    const [fileName, setFileName] = useState("");
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext)
    const handleSubmit = async () => {
        try {
            console.log("Submitted File")
            showModal(false); // Optionally close modal on success
        } catch (error) {
            console.error("Error creating file:", error);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-opacity-50">

            <div className="bg-white rounded-lg shadow-lg p-8 min-w-[500px] min-h-[300px] flex flex-col">
                <div className="self-end"> <CloseButton onClick={() => showModal(false)} /></div>
                <h1 className="text-xl font-bold mb-4">Add File</h1>
                <hr className="mb-4" />

                <div className="mb-4">
                    <label className="block font-medium mb-1">File Name</label>
                    <input
                        type="text"
                        className="w-full border rounded p-2"
                        placeholder="Enter file name"
                        value={fileName}
                        onChange={(e) => setFileName(e.target.value)}
                    />
                </div>
                <button
                    className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                    onClick={handleSubmit}
                >
                    Submit
                </button>

            </div>
        </div>
    );
}

export default CreateFileModal;