import React, { memo, useMemo, useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import type { OnChange } from "@monaco-editor/react";
import type { editor as MonacoEditor } from "monaco-editor";
import { useCodeEditorContext } from "../../context/CodeEditorContext";
import { useEffect } from "react";

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
  const { selectedFile, fileContent, setFileContent } = useCodeEditorContext();
  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);

  const resolvedLanguage = useMemo(() => {
    const ext = selectedFile?.split(".").pop() ?? "";
    return languageMap[ext] ?? "plaintext";
  }, [selectedFile]);

  const handleEditorChange: OnChange = useCallback(
    (value) => {
      // Only update context if user is typing
      setFileContent(value ?? "");
    },
    [setFileContent]
  );



  useEffect(() => {
    if (!fileContent || !selectedFile) return;
    let c = fileContent;
    c.trim()
      // normalize line endings
      .replace(/\r\n/g, "\n")
      // remove extra blank lines (keep one)
      .replace(/\n{2,}/g, "\n")
      // remove trailing spaces on each line
      .split("\n")
      .map((line) => line.replace(/\s+$/g, ""))
      .join("\n");
    setFileContent(c);
  }, [selectedFile]);

  return (
    <Editor
      height="80vh"
      language={resolvedLanguage}
      value={fileContent}
      onChange={handleEditorChange}
      onMount={(editor) => (editorRef.current = editor)}
      options={{
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: "on",
        scrollBeyondLastLine: false,
        padding: { top: 12 },
        smoothScrolling: true,
        formatOnType: true,
        formatOnPaste: true,
        wordWrap: "on",
      }}
      theme={theme}
    />
  );
};

export default memo(CodeEditor);
