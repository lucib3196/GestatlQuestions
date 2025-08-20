import React, { createContext, useState } from "react";

// Define proper union types
type RenderingType = "legacy" | "new";
type CodeRunningType = "javascript" | "python";

type GeneralSettingsContextType = {
    renderingSettings: RenderingType;
    setRenderingSettings: React.Dispatch<React.SetStateAction<RenderingType>>;
    codeRunningSettings: CodeRunningType;
    setCodeRunningSettings: React.Dispatch<React.SetStateAction<CodeRunningType>>;
};

// Create context with default values
export const QuestionSettingsContext = createContext<GeneralSettingsContextType>({
    renderingSettings: "legacy",
    setRenderingSettings: () => { },
    codeRunningSettings: "javascript",
    setCodeRunningSettings: () => { },
});

const QuestionSettingsProvider = ({ children }: { children: React.ReactNode }) => {
    const [renderingSettings, setRenderingSettings] = useState<RenderingType>("legacy");
    const [codeRunningSettings, setCodeRunningSettings] = useState<CodeRunningType>("javascript");

    return (
        <QuestionSettingsContext.Provider
            value={{
                renderingSettings,
                setRenderingSettings,
                codeRunningSettings,
                setCodeRunningSettings,
            }}
        >
            {children}
        </QuestionSettingsContext.Provider>
    );
};

export default QuestionSettingsProvider;
