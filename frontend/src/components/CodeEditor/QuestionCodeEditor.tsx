import { useEffect, useMemo, useState } from "react";
import { getFiles } from "../../api";
import { fetchFileContent, getFileNames, getLanguage } from "../../utils";
import type { FileData } from "../../types/types";
import CodeEditor from "./CodeEditorBase";

import { LogOutput } from "./LogPrint";
import { CodeEditorOptions } from "./CodeEditorOptions";
import { useQuestion } from "../../context/QuestionSelectionContext";

function QuestionCodeEditor() {
  // const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
  const { questionID: selectedQuestion } = useQuestion();
  const [filesData, setFileData] = useState<FileData[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [showLogOutput, setShowLogOutput] = useState(false);

  const [fileContent, setFileContent] = useState("");
  useEffect(() => {
    const id = String(selectedQuestion ?? "").trim();
    if (!id) {
      setFileData([]);
      return;
    }
    (async () => {
      const files = await getFiles(id);
      setFileData(files ?? []);
      const first = getFileNames(files ?? [])[0] ?? "";
      setSelectedFile(first);
    })();
  }, [selectedQuestion]);

  useEffect(
    () => setFileContent(fetchFileContent(selectedFile, filesData) ?? ""),
    [selectedFile, filesData]
  );

  return (
    <div className="flex flex-col items-center justify-center space-y-6">
      {/* Toolbar Options */}
      <CodeEditorOptions
        selectedFile={selectedFile}
        selectedQuestion={selectedQuestion}
        fileContent={fileContent}
      />

      {/* Editor */}
      <CodeEditor
        content={fileContent}
        language={getLanguage(selectedFile)}
        onChange={setFileContent}
      />

      {/* Logs Toggle */}
      <button
        className="rounded-md border-2 border-gray-300 px-4 py-2 text-sm font-medium hover:bg-gray-50"
        onClick={() => setShowLogOutput((prev) => !prev)}
      >
        {showLogOutput ? "Hide Logs" : "Show Logs"}
      </button>

      {showLogOutput && <LogOutput />}
    </div>
  );
}

export default QuestionCodeEditor;
