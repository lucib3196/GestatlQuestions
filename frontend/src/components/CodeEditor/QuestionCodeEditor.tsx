import CodeEditor from "./CodeEditorBase";
import { LogOutput } from "./LogPrint";
import { Loading } from "../Base/Loading";
import { useCodeEditorContext } from "../../context/CodeEditorContext";
import { CodeEditorToolBar } from "./CodeEditorToolBar";
import { useQuestionFiles } from "../../hooks/codeEditorHooks";
import { useState, useEffect } from "react";
import { getImageBase64FileData, isImageExt } from "../../utils/parsers";

export default function QuestionCodeEditor() {
  const { showLogs, selectedFile } = useCodeEditorContext();
  const { loading, filesData } = useQuestionFiles();
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedFile) {
      setImage(null);
      return;
    }
    if (isImageExt(selectedFile)) {
      const file = filesData.find((v) => v.filename === selectedFile);
      if (file) {
        const imageUrl = getImageBase64FileData(file);
        setImage(imageUrl);
      } else {
        setImage(null);
      }
    }
  }, [selectedFile, filesData]);

  if (loading) return <Loading />;

  return (
    <>
      <CodeEditorToolBar />
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
      {showLogs && <LogOutput />}
    </>
  );
}
