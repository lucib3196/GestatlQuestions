import { MyButton } from "../Base/Button";
import FileDropDown from "../Generic/FileDropDown";
import { useCodeEditorContext } from "./../../context/CodeEditorContext";
import { CodeSettings } from "../QuestionFilter/CodeSettings";
import { MyModal } from "../Base/MyModal";
import { useQuestionContext } from "../../context/QuestionContext";
import {
  useDeleteQuestionFile,
  useSaveQuestionFile,
  useUploadQuestionFiles,
} from "../../hooks/codeEditorHooks";
import { useState } from "react";
import { UploadCodeFile } from "./UploadCodeFiles";
import { DeleteCodeFile } from "./DeletedCodeFiles";
import QuestionUpdateForm from "../Forms/UpdateQuestionMeta";

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

  const { selectedQuestionID } = useQuestionContext();

  const { saveFile } = useSaveQuestionFile(() =>
    setRefreshKey((prev) => prev + 1)
  );
  const { deleteFile } = useDeleteQuestionFile(() =>
    setRefreshKey((prev) => prev + 1)
  );
  const { uploadFile } = useUploadQuestionFiles(() =>
    setRefreshKey((prev) => prev + 1)
  );

  const [showUpload, setShowUpload] = useState(false);
  const [showEditMeta, setShowEditMeta] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  return (
    <div className="flex flex-col w-full gap-4 my-4">
      {/* File Selector */}
      <div className="w-full">
        <FileDropDown
          fileNames={fileNames}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
        />
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap justify-between items-center gap-4 p-3 bg-gray-50 rounded-lg shadow-sm border border-gray-200">
        {/* Button Group */}
        <div className="flex flex-wrap gap-3 flex-1 justify-start">
          {/* Primary actions */}
          <MyButton
            name="Upload"
            className="min-w-[110px]"
            onClick={() => setShowUpload((prev) => !prev)}
          />
          <MyButton
            name="Save"
            className="min-w-[110px]"
            onClick={() =>
              saveFile(selectedQuestionID ?? "", selectedFile, fileContent)
            }
          />

          {/* Secondary actions */}
          <MyButton
            name="Delete"
            className="min-w-[110px]"
            onClick={() => setShowDelete((prev) => !prev)}
          />
          <MyButton
            name="Show Logs"
            color="secondary"
            className="min-w-[110px]"
            onClick={() => setShowLogs((prev) => !prev)}
          />
          <MyButton
            name="Edit Question Meta"
            color="success"
            className="min-w-[110px]"
            onClick={() => setShowEditMeta((prev) => !prev)}
          />
        </div>

        {/* Code Settings (aligned right) */}
        <div className="shrink-0">
          <CodeSettings
            setLanguage={setCodeRunningSettings}
            language={codeRunningSettings}
          />
        </div>
      </div>

      {/* Modals */}
      {showUpload && (
        <MyModal setShowModal={() => setShowUpload((prev) => !prev)}>
          <UploadCodeFile
            questionId={selectedQuestionID ?? ""}
            onSubmit={uploadFile}
          />
        </MyModal>
      )}

      {showEditMeta && (
        <MyModal setShowModal={() => setShowEditMeta((prev) => !prev)}>
          <QuestionUpdateForm />
        </MyModal>
      )}

      {showDelete && (
        <MyModal setShowModal={() => setShowDelete((prev) => !prev)}>
          <DeleteCodeFile
            questionId={selectedQuestionID ?? ""}
            filename={selectedFile}
            onSubmit={() => deleteFile(selectedQuestionID ?? "", selectedFile)}
          />
        </MyModal>
      )}
    </div>
  );
}
