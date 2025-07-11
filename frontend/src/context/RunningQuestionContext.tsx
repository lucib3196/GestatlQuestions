import React, { createContext, useState } from "react";

type RunningQuestionContextType = {
    selectedQuestion: string | null
    setSelectedQuestion: React.Dispatch<React.SetStateAction<string | null>>;
}

export const RunningQuestionSettingsContext = createContext<RunningQuestionContextType>({
    selectedQuestion: null,
    setSelectedQuestion: () => { }
})

const RunningQuestionProvider = ({ children }: { children: React.ReactNode }) => {
    const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null);
    return (
        <RunningQuestionSettingsContext.Provider value={{
            selectedQuestion,
            setSelectedQuestion
        }} >
            {children}
        </RunningQuestionSettingsContext.Provider>
    )
}

export default RunningQuestionProvider