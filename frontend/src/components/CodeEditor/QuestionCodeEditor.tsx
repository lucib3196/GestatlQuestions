import CodeEditor from "./CodeEditorBase";
import { LogOutput } from "./LogPrint";
import { Loading } from "../Base/Loading";
import { useCodeEditorContext } from "../../context/CodeEditorContext";
import { CodeEditorToolBar } from "./CodeEditorToolBar";
import { useQuestionFiles } from "../../hooks/codeEditorHooks";
import { useState, useEffect } from "react";



export default function QuestionCodeEditor() {
  const { showLogs, selectedFile, } = useCodeEditorContext();
  const { loading, filesData } = useQuestionFiles();
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedFile) {
      setImage(null);
      return;
    }

    const ext = selectedFile.split(".").at(-1)?.toLowerCase();
    if (ext === "png" || ext === "jpg" || ext === "jpeg") {
      const file = filesData.find((v) => v.filename === selectedFile);
      if (file && file.content && file.mime_type?.startsWith("image")) {
        setImage(`data:${file.mime_type};base64,${file.content}`);
      } else {
        setImage(null);
      }
    } else {
      setImage(null);
    }
  }, [selectedFile, filesData]);

  if (loading) return <Loading />;

  return (
    <>
      {/* Toolbar */}
      <div className="flex w-full items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-3">
        <CodeEditorToolBar />
      </div>

      {/* Editor or Image */}
      <div
        id="EditorContainer"
        className="w-full rounded-lg border border-gray-300 dark:border-gray-600 overflow-auto p-4 flex justify-center"
      >
        {image ? (
          <img
            src={image}
            alt={selectedFile ?? "decoded image"}
            className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-md"
          />
        ) : (
          <CodeEditor />
        )}
      </div>

      {/* Logs */}
      {showLogs && (
        <div className="w-full mt-4">
          <LogOutput />
        </div>
      )}
    </>
  );
}
