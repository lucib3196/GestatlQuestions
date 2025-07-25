import { useContext, useEffect, useState } from "react";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import CodeEditor from "./CodeEditor";

import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import type { SelectChangeEvent } from "@mui/material/Select";
import { SaveCodeButton, AddFileButton, CreateNewFileButton } from "../Buttons";

import api from "../../api";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";


type CodeFileDropDownProps = {
    fileNames: string[];
};

function NewCodeModal() {
    return (<div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 min-w-[500px] min-h-[500px]">
            <h1>Add File</h1>
            <hr></hr>
        </div>
        <FormControl />


    </div>)

}

function QuestionCodeEditor() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const [fileNames, setFileNames] = useState<string[]>([]);
    const [selectedFile, setSelectedFile] = useState<string>("");
    const [fileContent, setFileContent] = useState<string>("");

    const [createFile, setCreateFile] = useState<boolean>(false);

    // Fetch file names for the selected question
    const getFiles = async () => {
        try {
            const response = await api.get(`/local_questions/get_question_files/${selectedQuestion}`);
            setFileNames(response.data);
        } catch (error) {
            console.log("Error fetching file names");
        }
    };

    useEffect(() => {
        getFiles();
    }, [selectedQuestion]);

    // Update selected file when fileNames change
    useEffect(() => {
        setSelectedFile(fileNames[0] || "");
    }, [fileNames]);

    // Fetch file content when selectedFile changes
    const getFileContent = async () => {
        if (!selectedFile) {
            setFileContent("");
            return;
        }
        try {
            const response = await api.get(`/local_questions/get_question_file/${selectedQuestion}/${selectedFile}`);
            setFileContent(response.data);

        } catch (error) {
            console.log("Error fetching file content");
        }
    };

    const saveCode = async () => {
        try {
            api.post("/local_questions/update_file/", {
                title: selectedQuestion,
                filename: selectedFile,
                newcontent: fileContent
            })
        } catch (error) {
            console.error(error)
        }
    }

    const createNewFile = () => {
        console.log("Creating new file")
    }

    useEffect(() => {
        getFileContent();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedFile]);

    function CodeFileDropDown({ fileNames }: CodeFileDropDownProps) {
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
                        <MenuItem key={val} value={val}>{val}</MenuItem>
                    ))}
                </Select>
            </FormControl>
        );
    }

    return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <CodeFileDropDown fileNames={fileNames} />
            <div className="flex  flex-row justify-start gap-x-5">
                <SaveCodeButton disabled={false} onClick={() => saveCode()} />
                <AddFileButton disabled={false} onClick={() => console.log("Saving")} />
                <CreateNewFileButton disabled={false} onClick={() => setCreateFile((prev) => !prev)} />
            </div>
            <Paper className='z-0' sx={{ mt: 2, p: 2, backgroundColor: "#f5f5f5" }} >
                {/* Modal for creating a new file */}
                {createFile && (
                    <NewCodeModal />
                )}

                <CodeEditor content={fileContent as string} language={selectedFile.split(".").pop() || ""} onChange={value => setFileContent(value ?? "")} />
            </Paper>

        </Box>
    );
}

export default QuestionCodeEditor