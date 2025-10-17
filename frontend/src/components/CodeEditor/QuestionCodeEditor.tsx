import { useEffect, useState } from "react";
import { getLanguage } from "../../utils";
import type { FileData } from "../../types/types";
import CodeEditor from "./CodeEditorBase";
import { LogOutput } from "./LogPrint";
import { useQuestion } from "../../context/QuestionSelectionContext";
import { questionApi } from "../../api";
import { toast } from "react-toastify";
import FileDropDown from "../Generic/FileDropDown";
import { MyButton } from "../Base/Button";
import { Loading } from "../Base/Loading";

function QuestionCodeEditor() {
  const { questionID: selectedQuestion } = useQuestion();
  const [filesData, setFileData] = useState<FileData[]>([]);
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [showLogOutput, setShowLogOutput] = useState(false);
  const [fileContent, setFileContent] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchFiles = async () => {
      if (!selectedQuestion) {
        setFileData([]);
        setFileNames([]);
        setFileContent("");
        return;
      }

      setLoading(true);
      setFileData([]);
      setFileNames([]);
      setFileContent("");

      try {
        const response = await questionApi.getQuestionFiles({
          questionID: selectedQuestion,
        });
        setFileData(response);
      } catch (error) {
        console.error(error);
        toast.error("Could not get question files");
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, [selectedQuestion]);

  useEffect(() => {
    const names = filesData.map((v) => v.filename);
    setFileNames(names);
  }, [filesData]);

  useEffect(() => {
    const fd = filesData.find((v) => v.filename === selectedFile);
    setFileContent(fd?.content ?? "");
  }, [selectedFile, filesData,selectedQuestion]);


  if (loading)
    return <Loading />

  return (
    <div
      className="flex flex-col w-full max-w-4xl border border-gray-200 dark:border-gray-700 rounded-xl 
                    bg-white dark:bg-gray-900 shadow-sm p-6 space-y-6 transition-colors duration-200"
    >
      {/* Toolbar */}
      <div className="flex w-full items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-3">
        <div className="flex items-center gap-3">
          <span className="text-base font-semibold text-gray-800 dark:text-gray-200">
            Files
          </span>
          <FileDropDown
            fileNames={fileNames}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Placeholder for upcoming toolbar buttons */}
          <MyButton
            name={showLogOutput ? "Hide Logs" : "Show Logs"}
            onClick={() => setShowLogOutput((prev) => !prev)}
          />
        </div>
      </div>

      {/* Code Editor */}
      <div className="w-full rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
        <CodeEditor
          content={fileContent}
          language={getLanguage(selectedFile)}
          onChange={setFileContent}
        />
      </div>

      {/* Log Output */}
      {showLogOutput && (
        <div className="w-full mt-4">
          <LogOutput />
        </div>
      )}
    </div>
  );
}

export default QuestionCodeEditor;
