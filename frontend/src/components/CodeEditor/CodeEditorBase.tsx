import React, { memo, useMemo, useCallback, useRef, useEffect } from "react";
import Editor from "@monaco-editor/react";
import type { OnChange } from "@monaco-editor/react";
import type { editor as MonacoEditor } from "monaco-editor";
import { useCodeEditorContext } from "../../context/CodeEditorContext";
import { useState } from "react";

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


  return (
    <Editor
      height="80vh"
      language={resolvedLanguage}
      value={fileContent
        ?.trim()
        // normalize line endings
        .replace(/\r\n/g, "\n")
        // remove extra blank lines (keep one)
        .replace(/\n{2,}/g, "\n")
        // remove trailing spaces on each line
        .split("\n")
        .map(line => line.replace(/\s+$/g, ""))
        .join("\n")}


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