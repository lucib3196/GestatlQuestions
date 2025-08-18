import { useContext, useEffect, useState } from "react";

// Context
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import { useCallback } from "react";
// Components
import CodeEditor from "./CodeEditor";
import CreateFileModal from "./CreateFileModal";
import { SaveCodeButton, CreateFileButton, UploadFileButton } from "../Buttons";
import { UploadFileModal } from "./UploadFileModal";
// API
import api from "../../api";
import { toast } from 'react-toastify';
// MUI Components
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import type { SelectChangeEvent } from "@mui/material/Select";

type CodeFileDropDownProps = {
    fileNames: string[];
    selectedFile: string;
    setSelectedFile: (val: string) => void;
};


function toStringSafe(value: any) {
    if (value == null) return "";
    if (typeof value === "string") return value;
    return JSON.stringify(value)
}
function CodeFileDropDown({
    fileNames,
    selectedFile,
    setSelectedFile,
}: CodeFileDropDownProps) {
    const handleFileChange = (event: SelectChangeEvent) => {
        setSelectedFile(event.target.value as string);
    };

    return (
        <FormControl fullWidth size="small" sx={{ mt: 2 }}>
            <InputLabel id="code-file-select-label">File</InputLabel>
            <Select
                labelId="code-file-select-label"
                id="code-file-select"
                value={selectedFile}
                label="File"
                onChange={handleFileChange}
                sx={{ backgroundColor: "background.paper" }}
            >
                {fileNames.map((val) => (
                    <MenuItem key={val} value={val}>
                        {val}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
}

type FileData = {
    filename: string;
    content: string;
};
function QuestionCodeEditor() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const [filesData, setFileData] = useState<FileData[]>([]);

    const [fileNames, setFileNames] = useState<string[]>([]);
    const [selectedFile, setSelectedFile] = useState<string>("");
    const [fileContent, setFileContent] = useState<string>("");
    const [showAddFile, setShowAddFile] = useState(false);
    const [uploadFile, setUploadFile] = useState(false);

    const fetchFiles = useCallback(
        async (id: string) => {
            try {
                const res = await api.get(
                    `/db_questions/get_question_files/${encodeURIComponent(id)}`
                );
                setFileData(Array.isArray(res.data) ? res.data : []);
            } catch (err) {
                console.error("Failed to fetch file names:", err);
                setFileData([]);
            }
        },
        [api]
    );

    useEffect(() => {
        const id = String(selectedQuestion ?? "").trim();
        if (!id) {
            setFileData([]);
            return;
        }
        fetchFiles(id);
    }, [selectedQuestion, fetchFiles]);

    useEffect(() => {
        const names = (filesData ?? [])
            .map((f) => (typeof f?.filename === "string" ? f.filename : null))
            .filter(Boolean) as string[];
        setFileNames(names);
    }, [filesData]);

    useEffect(() => {
        if (fileNames.length > 0) {
            setSelectedFile(fileNames[0]);
        }
    }, [fileNames]);

    const fetchFileContent = (filename: string) => {
        try {
            const match = filesData?.find((f) => f.filename === filename);
            if (!match) {
                console.warn(`File not found: ${filename}`);
                setFileContent("");
                return;
            }
            setFileContent(toStringSafe(match.content) ?? "");

        } catch (err) {
            console.error("Failed to fetch file content:", err);
        }
    };
    useEffect(() => {
        if (selectedFile) {
            fetchFileContent(selectedFile);
        } else {
            setFileContent("");
        }
    }, [selectedFile]);


    const saveCode = async () => {
        try {
            await api.post("/db_questions/update_file/", {
                title: selectedQuestion,
                filename: selectedFile,
                newcontent: fileContent,
            });

            toast.success("Code Saved Succesfully")
        } catch (err) {
            toast.error("Code Not Saved")
        }
    };


    const getLanguage = () =>
        selectedFile?.split(/[_\.]/).pop() || "";
    console.log(fileContent)
    return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <CodeFileDropDown
                fileNames={fileNames}
                selectedFile={selectedFile}
                setSelectedFile={setSelectedFile}
            />

            <div className="flex flex-row justify-start gap-x-5">
                <SaveCodeButton onClick={saveCode} />
                <CreateFileButton onClick={() => setShowAddFile((prev) => !prev)} />
                <UploadFileButton onClick={() => setUploadFile((prev) => !prev)} />
            </div>

            <Paper className="z-0" sx={{ mt: 2, p: 2, backgroundColor: "#f5f5f5" }}>
                <CodeEditor
                    content={fileContent}
                    language={getLanguage()}
                    onChange={(value) => setFileContent(value ?? "")}
                />
                {showAddFile && <CreateFileModal showModal={setShowAddFile} />}
                {uploadFile && <UploadFileModal setShowModal={setUploadFile} />}
            </Paper>
        </Box>
    );
}

export default QuestionCodeEditor;
