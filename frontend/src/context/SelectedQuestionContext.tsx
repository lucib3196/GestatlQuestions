import React, { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { QuestionAPI } from "../api/questionCrud";
import type { QuestionMeta } from "../types/questionTypes";


type SelectedQuestionContextType = {
    selectedQuestionID: string | null;
    setSelectedQuestionID: React.Dispatch<React.SetStateAction<string | null>>;
    questionMeta: QuestionMeta | null,
    setQuestionMeta: React.Dispatch<React.SetStateAction<QuestionMeta | null>>
};

export const SelectedQuestionContext = createContext<SelectedQuestionContextType>({
    selectedQuestionID: null,
    setSelectedQuestionID: () => { },
    questionMeta: null,
    setQuestionMeta: () => { },
});

export const SelectedQuestionProvider = ({
    children,
}: {
    children: ReactNode;
}) => {
    const [selectedQuestionID, setSelectedQuestionID] = useState<string | null>(
        null
    );
    const [questionMeta, setQuestionMeta] = useState<QuestionMeta | null>(null);

    const fetchQuestionMeta = useCallback(async () => {
        if (!selectedQuestionID) return;
        try {
            const retrieved = await QuestionAPI.getQuestion(selectedQuestionID);
            setQuestionMeta(retrieved);
        } catch (error) {
            console.error("❌ Failed to fetch question:", error);
        }
    }, [selectedQuestionID]);

    useEffect(() => {
        fetchQuestionMeta();
    }, [fetchQuestionMeta]);

    return (
        <SelectedQuestionContext.Provider
            value={{
                selectedQuestionID,
                setSelectedQuestionID,
                questionMeta,
                setQuestionMeta,
            }}
        >
            {children}
        </SelectedQuestionContext.Provider>
    );
};

export function useSelectedQuestion() {
    const context = useContext(SelectedQuestionContext);
    if (context === undefined) {
        throw new Error("useSelectedQuestion must be used within a SelectedQuestionProvider");
    }
    return context;
}

export default SelectedQuestionProvider;
