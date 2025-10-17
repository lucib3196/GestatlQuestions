import React, { memo, useMemo, useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import type { OnChange } from "@monaco-editor/react";
import type { editor as MonacoEditor } from "monaco-editor";
interface CodeEditorProps {
  content: string;
  language: string /** Language key: 'js', 'py', etc. */;
  onChange?: (value: string) => void;
  height?: string;
}
const languageMap: Record<string, string> = {
  js: "javascript",
  py: "python",
  json: "json",
  html: "html",
};

interface CodeEditorProps {
  content: string;
  language: string;
  onChange?: (value: string) => void;
  theme: string
}

const CodeEditor: React.FC<CodeEditorProps> = ({ content, language, onChange,theme="vs-light" }) => {
  const resolvedLanguage = useMemo(() => languageMap[language] ?? "plaintext", [language]);

  const handleEditorChange: OnChange = useCallback(
    (value) => onChange?.(value ?? ""),
    [onChange]
  );

  const editorRef = useRef<MonacoEditor.IStandaloneCodeEditor | null>(null);

  return (
    <div className="w-full  overflow-auto">
      <Editor
      height={"80vh"}
        language={resolvedLanguage}
        value={content}
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
    </div>
  );
};

export default memo(CodeEditor);
