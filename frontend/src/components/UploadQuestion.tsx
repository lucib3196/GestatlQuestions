import React, { useState, useEffect } from "react";
import { MdDriveFolderUpload } from "react-icons/md";
import JSZip, { file } from "jszip";

const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) {
        return "0 Bytes";
    }
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

const handleZipFiles = async (files: FileList) => {
    const zip = new JSZip();
    if (!files) {
        return;
    }

    for (let i = 0; i < files.length; i++) {
        let file = files.item(i);
        if (!file) {
            return;
        }
        zip.file(`${i + 1}_${file.name}`, file);
    }
    const zipContent = await zip.generateAsync({ type: "blob" });
    try {
        const formData = new FormData();
        formData.append("files", zipContent, "zippedfile.zip");

    } catch (error) {
        console.log(error);
        console.log("Could not upload files");
    }
};

// Takes in a zip file
export function UploadQuestion() {
    const [fileList, setFileList] = useState<FileList | null>(null);

    const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;

        if (!files) {
            return;
        }
        console.log("Submitting Files");

        for (let i = 0; i < files.length; i++) {
            let file = files.item(i);
            if (!file) {
                return;
            }
            Object.assign(file, {
                preview: URL.createObjectURL(file),
                formattedSize: formatBytes(file.size),
            });
        }
        setFileList(files);
        handleZipFiles(files);
    };

    useEffect(() => {
        if (fileList) {
            console.log("fileList updated:", fileList);
        }
    }, [fileList]);

    return (
        <button className="relative  flex flex-row items-center gap-x-2 justify-center text-center hover:bg-primary-blue bg-accent-sky text-text-primary hover:text-surface border rounded-md px-2 py-2 font-bold">
            <MdDriveFolderUpload className="md:size-8" /> Upload Question
            <input
                type="file"
                className="absolute inset-0 opacity-0 cursor-pointer"
                name="files"
                multiple
                onChange={handleUpload}
            />
        </button>
    );
}
