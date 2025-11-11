import React, { memo, useMemo, useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import type { OnChange } from "@monaco-editor/react";
import type { editor as MonacoEditor } from "monaco-editor";
import { useCodeEditorContext } from "../../context/CodeEditorContext";
import { useEffect } from "react";
import { debounce } from "lodash";


const languageMap: Record<string, string> = {
  js: "javascript",
  py: "python",
  json: "json",
  html: "html",
};

interface CodeEditorProps {
  theme?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ theme = "vs-light" }) => {
  const { selectedFile, fileContent, setFileContent, } = useCodeEditorContext();
  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);

  const resolvedLanguage = useMemo(() => {
    const ext = selectedFile?.split(".").pop() ?? "";
    return languageMap[ext] ?? "plaintext";
  }, [selectedFile]);

  const handleEditorChange: OnChange = useCallback(
    debounce((value?: string) => setFileContent(value ?? ""), 600),
    [selectedFile]
  );

  useEffect(() => {
    if (!selectedFile || !fileContent) return;

    const cleaned = fileContent
      .trim()
      .replace(/\r\n/g, "\n")
      .replace(/\n{2,}/g, "\n")
      .split("\n")
      .map((line) => line.replace(/\s+$/g, ""))
      .join("\n");

    // Only update if cleaned version differs (prevents cursor jump)
    if (cleaned !== fileContent) {
      setFileContent(cleaned);
    }
  }, [selectedFile]);

  return (
    <Editor
      height="80vh"
      language={resolvedLanguage}
      value={fileContent}
      onChange={handleEditorChange}
      onMount={(editor) => {
        console.log("Monaco mounted");
        editorRef.current = editor;
      }}
      options={{
        // automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: "on",
        // scrollBeyondLastLine: false,
        padding: { top: 12 },
        smoothScrolling: true,
        // formatOnType: true,
        // formatOnPaste: true,
        // wordWrap: "on",
      }}
      theme={theme}
    />
  );
};

export default memo(CodeEditor);
