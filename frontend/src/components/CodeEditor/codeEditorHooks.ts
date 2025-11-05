import { useCodeEditorContext } from "./../../context/CodeEditorContext";
import { useState, useCallback, useEffect } from "react";
import { useSelectedQuestion } from "../../context/SelectedQuestionContext";
import { QuestionAPI } from "./../../api/questionCrud";
import { toast } from "react-toastify";
import type { FileData } from "../../types/questionTypes";

export function useQuestionFiles() {
  const { setFileNames, selectedFile, setFileContent, refreshKey } =
    useCodeEditorContext();
  const { selectedQuestionID } = useSelectedQuestion();

  const [filesData, setFileData] = useState<FileData[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = useCallback(async () => {
    if (!selectedQuestionID) {
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
      const response = await QuestionAPI.getQuestionFiles(selectedQuestionID);
      setFileData(response);
    } catch (error) {
      console.error(error);
      toast.error("Could not get question files");
    } finally {
      setLoading(false);
    }
  }, [selectedQuestionID, setFileNames, setFileContent]);
  useEffect(() => {
    fetchFiles();
  }, [fetchFiles, refreshKey]);
  useEffect(() => {
    const fd = filesData.find((v) => v.filename === selectedFile);
    setFileContent(fd?.content ?? "");
  }, [selectedFile, filesData, setFileContent]);

  useEffect(() => {
    setFileNames(filesData.map((v) => v.filename));
  }, [filesData, setFileNames]);

  return { filesData, loading };
}

export function useSaveQuestionFile(onRefresh?: () => void) {
  const [loading, setLoading] = useState(false);

  const saveFile = useCallback(
    async (questionID: string, filename: string, content: string) => {
      try {
        setLoading(true);
        await QuestionAPI.updateFileContent(questionID, filename, content);
        toast.success("File saved successfully!");
        onRefresh?.();
      } catch (error) {
        console.error(error);
        toast.error("Could not save file.");
      } finally {
        setLoading(false);
      }
    },
    [onRefresh]
  );

  return { saveFile, loading };
}

export function useUploadQuestionFiles(onRefresh?: () => void) {
  const [loading, setLoading] = useState(false);

  const uploadFile = useCallback(
    async (questionID: string, files: File[]) => {
      try {
        setLoading(true);
        await QuestionAPI.uploadFiles(questionID, files);
        toast.success("File uploaded successfully!");
        onRefresh?.();
      } catch (error) {
        console.error(error);
        toast.error("Could not upload file.");
      } finally {
        setLoading(false);
      }
    },
    [onRefresh]
  );

  return { uploadFile, loading };
}

// export function useDeleteQuestionFile(onRefresh?: () => void) {
//   const [loading, setLoading] = useState(false);

//   const deleteFile = useCallback(
//     async (questionID: string, filename: string) => {
//       try {
//         setLoading(true);
//         await QuestionAPI.deleteFile(questionID, filename);
//         toast.success("File deleted successfully!");
//         onRefresh?.();
//       } catch (error) {
//         console.error(error);
//         toast.error("Could not delete file.");
//       } finally {
//         setLoading(false);
//       }
//     },
//     [onRefresh]
//   );

//   return { deleteFile, loading };
// }
