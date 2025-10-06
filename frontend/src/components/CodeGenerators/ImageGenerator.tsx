
import React, { useState } from "react";
import ModGenerators from "./BaseTemplate";
import api from "../../api/client";
import { toast } from "react-toastify";
import UploadFilesButton from "../Generic/UploadFiles";
const ImageGeneratorConst = {
    name: "Visual Extract",
};

const examples = [
    {
        name: "Textbook Solutions",
        text: "Officially published problems and solutions ensure high accuracy.",
    },
    {
        name: "Handwritten Solutions",
        text: "Personal notes or handwritten solutions will be effectively processed.",
    },
    {
        name: "Lecture Materials",
        text: "Slides or instructional content from lectures can be used to create modules.",
    },
];

const FileUploadForm: React.FC = () => {
    const [fileList, setFileList] = useState<File[]>([]);
    const [loading, setLoading] = useState<boolean>(false);




    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!fileList) return;

        const formData = new FormData();

        for (let i = 0; i < fileList.length; i++) {
            formData.append("files", fileList[i]);
        }

        setLoading(true);

        try {
            const token = localStorage.getItem("access_token");
            if (!token) {
                toast.error("Error: Must Be Logged In")
                return;
            }
            const response = await api.post(
                "/codegenerator/v5/image_gen",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            toast.success("Generation Successful")
        } catch (error) {
            toast.error(`Error submitting form ${error}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
            <form onSubmit={handleSubmit} encType="multipart/form-data" className="space-y-4">

                <UploadFilesButton onFilesSelected={setFileList} />
                {fileList.length > 0 && (
                    <ul className="mt-4 space-y-2 text-sm text-gray-700">
                        {fileList.map((file, idx) => (
                            <li
                                key={idx}
                                className="flex justify-between items-center bg-gray-100 px-3 py-2 rounded-md"
                            >
                                <span className="font-medium">{file.name}</span>
                                <span className="text-xs text-gray-500">
                                    {Math.round(file.size / 1024)} KB
                                </span>
                            </li>
                        ))}
                    </ul>
                )}
                <button
                    type="submit"
                    className={`w-full py-2 px-4 rounded bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors duration-200 ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
                    disabled={loading}
                >
                    {loading ? "Generating..." : "Generate"}
                </button>
            </form>
        </div>
    );
};

export default function ImageGenerator() {
    return (
        <ModGenerators
            title={ImageGeneratorConst.name}
            subtitle="Upload your images below to generate personalized modules instantly."
            examples={examples}
            inputComponent={<FileUploadForm />}
        />
    );
}
