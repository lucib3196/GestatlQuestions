import React, { createContext, useContext, useState } from "react";
import type { CodeLanguage } from "../types/settingsType";

type CodeEditorContext = {
    fileNames: string[];
    setFileNames: React.Dispatch<React.SetStateAction<string[]>>;
    selectedFile: string;
    setSelectedFile: React.Dispatch<React.SetStateAction<string>>;

    fileContent: string;
    setFileContent: React.Dispatch<React.SetStateAction<string>>;

    logs: string[];
    setLogs: React.Dispatch<React.SetStateAction<string[]>>;
    showLogs: boolean;
    setShowLogs: React.Dispatch<React.SetStateAction<boolean>>

    codeRunningSettings: CodeLanguage;
    setCodeRunningSettings: React.Dispatch<React.SetStateAction<CodeLanguage>>;

    refreshKey: number;
    setRefreshKey: React.Dispatch<React.SetStateAction<number>>;
};

export const CodeEditorContex = createContext<CodeEditorContext>({
    fileNames: [],
    setFileNames: () => { },
    selectedFile: "",
    setSelectedFile: () => { },

    fileContent: "",
    setFileContent: () => { },

    logs: [],
    setLogs: () => { },
    showLogs: false,
    setShowLogs: () => { },
    codeRunningSettings: "javascript",
    setCodeRunningSettings: () => { },

    refreshKey: 0,
    setRefreshKey: () => { }
});

const CodeEditorProvider = ({ children }: { children: React.ReactNode }) => {
    const [logs, setLogs] = useState<string[]>([]);
    const [fileNames, setFileNames] = useState<string[]>([]);
    const [selectedFile, setSelectedFile] = useState<string>("");
    const [fileContent, setFileContent] = useState<string>("");
    const [codeRunningSettings, setCodeRunningSettings] =
        useState<CodeLanguage>("javascript");
    const [showLogs, setShowLogs] = useState<boolean>(false)
    const [refreshKey, setRefreshKey] = useState(0);
    
    
    return (
        <CodeEditorContex.Provider
            value={{
                fileNames,
                setFileNames,
                selectedFile,
                setSelectedFile,
                codeRunningSettings,
                setCodeRunningSettings,
                fileContent,
                setFileContent,
                logs,
                setLogs,
                showLogs,
                setShowLogs,
                refreshKey,
                setRefreshKey
            }}
        >
            {children}
        </CodeEditorContex.Provider>
    );
};
export default CodeEditorProvider;

export function useCodeEditorContext() {
    const context = useContext(CodeEditorContex);
    if (context === undefined) {
        throw new Error(
            "useSelectedQuestion must be used within a SelectedQuestionProvider"
        );
    }
    return context;
}
