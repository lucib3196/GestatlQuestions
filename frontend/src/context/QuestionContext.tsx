import { createContext, useContext, useState, type Dispatch, type ReactNode } from "react";
import type { QuestionMeta } from "../types/questionTypes";




type QuestionContextType = {
    questions: QuestionMeta[];
    setQuestions: Dispatch<React.SetStateAction<QuestionMeta[]>>;
};

export const QuestionContext = createContext<QuestionContextType | null>(null);

export function QuestionProvider({ children }: { children: ReactNode }) {
    const [questions, setQuestions] = useState<QuestionMeta[]>([]);

    return (
        <QuestionContext.Provider value={{ questions, setQuestions }}>
            {children}
        </QuestionContext.Provider>
    );
}


export function useQuestionContext() {
    const context = useContext(QuestionContext);

    if (!context) {
        throw new Error(
            "useQuestionContext must be used within a <QuestionProvider>"
        );
    }

    return context;
}