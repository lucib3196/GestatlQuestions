import { MyModal } from "../Generic/MyModal";
import { useContext, useState } from "react";
import api from "../../api/api";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
type UploadFileModalProps = {
    setShowModal: (visible: boolean) => void;
};


export function UploadFileModal({ setShowModal }: UploadFileModalProps) {
    const [isImage, setIsImage] = useState(false);
    const [fileList, setFileList] = useState<FileList | null>(null);
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFileList(e.target.files);
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!fileList) return;

        const formData = new FormData();
        for (let i = 0; i < fileList.length; i++) {
            formData.append("files", fileList[i]);
        }

        try {
            const response = await api.post(
                `/file/upload_file`,
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );
            console.log("Uploaded Successfully", response.data);
            setShowModal(false); // Close modal on success
        } catch (error) {
            console.error("Error submitting form:", error);
        }
    };

    return (
        <MyModal setShowModal={setShowModal}>
            <h1 className="text-xl font-bold mb-4">Upload File</h1>
            <hr className="mb-4" />
            <form
                onSubmit={handleSubmit}
                className="bg-white shadow-md rounded-lg px-8 pt-6 pb-8 mb-4 border border-gray-200"
            >
                <div className="mb-6 flex items-center space-x-3">
                    <input
                        type="checkbox"
                        id="isImageCheckbox"
                        checked={isImage}
                        onChange={() => setIsImage((prev) => !prev)}
                        className="w-4 h-4 text-indigo-600 border-gray-300 rounded"
                    />
                    <label htmlFor="isImageCheckbox" className="text-sm font-medium text-gray-700">
                        This is an image
                    </label>
                </div>

                <input
                    type="file"
                    name="files"
                    multiple
                    onChange={handleFileChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
                />

                <button
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded shadow"
                    type="submit"
                >
                    Upload
                </button>
            </form>
        </MyModal>
    );
}
