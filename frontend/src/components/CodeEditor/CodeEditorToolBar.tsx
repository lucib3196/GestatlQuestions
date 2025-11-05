import { MyButton } from "../Base/Button";
import FileDropDown from "../Generic/FileDropDown";
import { useCodeEditorContext } from "./../../context/CodeEditorContext";
import { CodeSettings } from "../QuestionFilter/CodeSettings";
import { MyModal } from "../Base/MyModal";
import { useSelectedQuestion } from "../../context/SelectedQuestionContext";
import { useSaveQuestionFile, useUploadQuestionFiles } from "./codeEditorHooks";
import { useState } from "react";
import { UploadCodeFile } from "./UploadCodeFiles";



export function CodeEditorToolBar() {
    const {
        fileNames,
        selectedFile,
        setSelectedFile,
        setCodeRunningSettings,
        codeRunningSettings,
        fileContent,
        setRefreshKey,
        setShowLogs,
    } = useCodeEditorContext();
    const { selectedQuestionID } = useSelectedQuestion();
    const { saveFile } = useSaveQuestionFile(() =>
        setRefreshKey((prev) => prev + 1)
    );
    const [showUpload, setShowUpload] = useState(false);
    const [showEditMeta, setShowEditMeta] = useState(false);
    const { uploadFile } = useUploadQuestionFiles()

    return (
        <div className="flex flex-col w-full gap-y-4 my-2">
            {/* Dropdown */}
            <div className="w-full">
                <FileDropDown
                    fileNames={fileNames}
                    selectedFile={selectedFile}
                    setSelectedFile={setSelectedFile}
                />
            </div>

            {/* Toolbar Buttons */}
            <div className="flex flex-wrap justify-between items-center gap-3 w-full">
                <div className="flex flex-wrap gap-3 flex-1 justify-between">
                    <MyButton
                        name="Upload"
                        className="flex-1 min-w-20"
                        onClick={() => setShowUpload((prev) => !prev)}
                    />
                    <MyButton
                        name="Save"
                        className="flex-1 min-w-20"
                        onClick={() =>
                            saveFile(selectedQuestionID ?? "", selectedFile, fileContent)
                        }
                    />
                    <MyButton name="Delete" className="flex-1 min-w-20" />
                    <MyButton
                        name="Show Logs"
                        onClick={() => setShowLogs((prev) => !prev)}
                        className="flex-1 min-w-20"
                    />
                    <MyButton
                        name="Update Question Meta"
                        className="flex-1 min-w-20"
                        onClick={() => setShowEditMeta((prev) => !prev)}
                    />
                </div>

                {/* Code Settings on the right */}
                <div className="shrink-0">
                    <CodeSettings
                        setLanguage={setCodeRunningSettings}
                        language={codeRunningSettings}
                    />
                </div>

                {showUpload && (
                    <MyModal setShowModal={() => setShowUpload((prev) => !prev)}>
                        <UploadCodeFile questionId={selectedQuestionID ?? ""} onSubmit={uploadFile} />
                    </MyModal>
                )}
                {showEditMeta && (
                    <MyModal setShowModal={() => setShowEditMeta((prev) => !prev)}>
                        <div>Meta</div>
                    </MyModal>
                )}
            </div>
        </div>
    );
}
