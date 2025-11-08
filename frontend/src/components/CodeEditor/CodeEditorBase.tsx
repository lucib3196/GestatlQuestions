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
  const [cleanedContent, setCleanedContent] = useState(fileContent);
  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);

  const resolvedLanguage = useMemo(() => {
    const ext = selectedFile?.split(".").pop() ?? "";
    return languageMap[ext] ?? "plaintext";
  }, [selectedFile]);

  const handleEditorChange: OnChange = useCallback(
    (value) => setFileContent(value ?? ""),
    [setFileContent]
  );

  // // ✅ Clean only when a *new file* is selected
  // useEffect(() => {
  //   if (!fileContent || !selectedFile) return;

  //   let c = fileContent;

  //   console.log("Cleaning new file:", selectedFile);

  //   if (resolvedLanguage === "html" && typeof fileContent === "string") {
  //     try {
  //       c = fileContent
  //         .split("\n")
  //         .map(line => line.trimEnd())
  //         .filter(line => line.length > 0)
  //         .join("");
  //     } catch (err) {
  //       console.error("HTML minify failed:", err);
  //     }
  //   }

  //   setCleanedContent(c);
  // }, [selectedFile]); // ← only runs when file changes

  // // Keep editor content in sync when switching files
  // useEffect(() => {
  //   // When selectedFile changes, reset file content to cleanedContent
  //   setFileContent(cleanedContent);
  // }, [cleanedContent]);

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