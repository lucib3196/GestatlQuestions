import React, { memo, useMemo, useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import type { OnChange } from "@monaco-editor/react";

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

const CodeEditor: React.FC<CodeEditorProps> = ({
  content,
  language,
  onChange,
  height = "60vh",
}) => {
  // Determine the editor's language, falling back to plaintext
  const resolvedLanguage = useMemo(
    () => languageMap[language] ?? "plaintext",
    [language]
  );

  // Handle changes in the editor
  const handleEditorChange: OnChange = useCallback(
    (value) => {
      onChange?.(value ?? "");
    },
    [onChange]
  );
  const editorRef = useRef(null);

  function handleEditorDidMount(editor: any) {
    editorRef.current = editor;
  }
  return (
    <>
      <Editor
        height={height}
        language={resolvedLanguage}
        value={content}
        onChange={handleEditorChange}
        options={{
          automaticLayout: true,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: "on",
        }}
        onMount={handleEditorDidMount}
      />
    </>
  );
};

export default memo(CodeEditor);
