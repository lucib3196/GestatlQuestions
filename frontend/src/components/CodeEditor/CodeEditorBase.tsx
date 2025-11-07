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
  const resolvedLanguage = useMemo(
    () => languageMap[selectedFile?.split(".").at(-1) ?? ""] ?? "plaintext",
    [selectedFile]
  );

  const handleEditorChange: OnChange = useCallback(
    (value) => setFileContent(value ?? ""),
    [setFileContent]
  );
  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    async function clean() {
      let c = fileContent;

      if (resolvedLanguage === "html") {
        try {
          // only load dynamically in browser-safe way
          c = fileContent
            .split("\n")
            .map((line) => line.trim())
            .filter(Boolean)
            .join("");
        } catch (err) {
          console.error("Minify failed (browser env):", err);
          c = fileContent;
        }
      }

      setCleanedContent(c);
    }

    clean();
  }, [selectedFile]);


  return (
    <Editor
      height={"80vh"}
      language={resolvedLanguage}
      value={cleanedContent}
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
      }}
      theme={theme}
    />
  );
};

export default memo(CodeEditor);
