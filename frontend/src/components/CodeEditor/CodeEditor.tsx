import React, { memo, useMemo, useCallback, useRef } from 'react';
import Editor from '@monaco-editor/react';
import type { OnChange } from '@monaco-editor/react';

interface CodeEditorProps {
    /** Initial or current editor content */
    content: string;
    /** Language key: 'js', 'py', etc. */
    language: string;
    /** Callback when content changes */
    onChange?: (value: string | undefined) => void;
    /** Editor height (default '60vh') */
    height?: string;
}

// Map shorthand keys to Monaco language identifiers
const languageMap: Record<string, string> = {
    js: 'javascript',
    py: 'python',
    json: "json",
    html: "html"
};

const CodeEditor: React.FC<CodeEditorProps> = ({
    content,
    language,
    onChange,
    height = '60vh',
}) => {
    // Determine the editor's language, falling back to plaintext
    const resolvedLanguage = useMemo(
        () => languageMap[language] ?? 'plaintext',
        [language]
    );

    // Handle changes in the editor
    const handleEditorChange: OnChange = useCallback(
        (value) => {
            onChange?.(value);
        },
        [onChange]
    );
    const editorRef = useRef(null);

    function handleEditorDidMount(editor, monaco) {
        editorRef.current = editor;
    }
    function formatCode() {
        if (editorRef.current) {
            editorRef.current.getAction("editor.action.formatDocument").run();
        }
    }

    return (
        <>
            <button onClick={formatCode}>Format Code</button>
            <Editor
                height={height}
                language={resolvedLanguage}
                value={content}

                onChange={handleEditorChange}
                options={{
                    automaticLayout: true,
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                }}

                onMount={handleEditorDidMount}
            />
        </>
    );
};

export default memo(CodeEditor);
