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
  }, [selectedFile, filesData, selectedQuestion]);

  const handleSave = async () => {
    if (!selectedQuestion) return;
    console.log("I am clicked")
    try {
      await questionApi.saveFileContent(
        selectedFile,
        fileContent,
        selectedQuestion
      );
    } catch (error) {
      toast.error("Could not save code");
    }
  };

  if (loading) return <Loading />;

  return (
    <>
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
          <MyButton
            name={"Save"}
            color="secondary"
            className="!bg-blue-500 text-white"
            onClick={handleSave}
          />
        </div>
      </div>

      {/* Code Editor */}
      <div className="w-full  rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
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
    </>
  );
}

export default QuestionCodeEditor;
