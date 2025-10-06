import React, { createContext, useState } from "react";
import { getSettings } from "../api";
import type { CodeLanguage, QuestionStorage, RenderingType } from "../types/settingsType";
// Define proper union types


import { useEffect } from "react";

type GeneralSettingsContextType = {
    renderingType: RenderingType;
    setRenderingType: React.Dispatch<React.SetStateAction<RenderingType>>;
    codeRunningSettings: CodeLanguage;
    setCodeRunningSettings: React.Dispatch<React.SetStateAction<CodeLanguage>>;
    questionStorage: QuestionStorage,
};

// Create context with default values
export const QuestionSettingsContext = createContext<GeneralSettingsContextType>({
    renderingType: "legacy",
    setRenderingType: () => { },
    codeRunningSettings: "javascript",
    setCodeRunningSettings: () => { },
    questionStorage: null

});

const QuestionSettingsProvider = ({ children }: { children: React.ReactNode }) => {
    const [renderingType, setRenderingType] = useState<RenderingType>("legacy");
    const [codeRunningSettings, setCodeRunningSettings] = useState<CodeLanguage>("javascript");
    const [questionStorage, setQuestionStorage] = useState<QuestionStorage>(null)

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const data = await getSettings();
                setQuestionStorage(data);
            } catch (err) {
                console.error("Failed to fetch settings", err);
            }
        };

        fetchSettings();
    }, []); // run once 
    return (
        <QuestionSettingsContext.Provider
            value={{
                renderingType,
                setRenderingType,
                codeRunningSettings,
                setCodeRunningSettings,
                questionStorage
            }}
        >
            {children}
        </QuestionSettingsContext.Provider>
    );
};

export default QuestionSettingsProvider;
