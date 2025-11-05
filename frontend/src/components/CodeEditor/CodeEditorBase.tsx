import React, { memo, useMemo, useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import type { OnChange } from "@monaco-editor/react";
import type { editor as MonacoEditor } from "monaco-editor";
import { useCodeEditorContext } from "../../context/CodeEditorContext";

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
  const resolvedLanguage = useMemo(
    () => languageMap[selectedFile?.split(".").at(-1) ?? ""] ?? "plaintext",
    [selectedFile]
  );

  const handleEditorChange: OnChange = useCallback(
    (value) => setFileContent(value ?? ""),
    [setFileContent]
  );

  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);

  return (
    <Editor
      height={"80vh"}
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
      }}
      theme={theme}
    />
  );
};

export default memo(CodeEditor);
