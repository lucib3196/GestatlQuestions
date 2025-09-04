import React, { createContext, useState } from "react";

type CodeLogsContextType = {
    logs: string[]
    setLogs: React.Dispatch<React.SetStateAction<string[]>>;
}

export const CodeLogsSettings = createContext<CodeLogsContextType>({
    logs: [],
    setLogs: () => { }
})


const LogsProvider = ({ children }: { children: React.ReactNode }) => {
    const [logs, setLogs] = useState<string[]>([])
    return (
        <CodeLogsSettings.Provider value={{
            logs, setLogs
        }}>
            {children}
        </CodeLogsSettings.Provider>
    )
}
export default LogsProvider