import { CodeLogsSettings } from "../../context/CodeLogsContext";

import { useContext } from "react";

interface LogOutputProps {
    filename?: string;
}

export function LogOutput({ filename }: LogOutputProps) {
    const { logs } = useContext(CodeLogsSettings) ?? { logs: [] };

    return (
        <div className="w-full border-gray-500 border-2 bg-white p-4">
            <h1>Output Logs <hr className="my-3" /></h1>
            {filename && (
                <div className="mb-2 text-sm text-gray-700">
                    Showing logs for: <strong>{filename}</strong>
                </div>
            )}
            <div className="max-h-64 overflow-y-auto bg-gray-50 p-2 rounded-md">
                {(logs.length > 0 ? logs : ["No logs available"]).map((log, idx) => (
                    <p key={idx} className="text-xs font-mono text-gray-800">
                        {log}
                    </p>
                ))}
            </div>
        </div>
    );
}