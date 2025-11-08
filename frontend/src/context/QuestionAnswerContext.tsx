import React, { createContext, useContext, useState } from "react";


type Answers = Record<string, string | number>;

type QuestionAnswersContextType = {
    answers: Answers
    setAnswer: (name: string, value: string) => void
}

const QuestionAnswersContext = createContext<QuestionAnswersContextType | null>(null)

export const QuestionAnswersProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [answers, setAnswers] = useState<Answers>({});

    const setAnswer = (name: string, value: string) => {
        setAnswers((prev) => ({ ...prev, [name]: value }));
    };

    return (
        <QuestionAnswersContext.Provider value={{ answers, setAnswer }}>
            {children}
        </QuestionAnswersContext.Provider>
    );
};

export const useQuestionAnswers = () => {
    const ctx = useContext(QuestionAnswersContext);
    if (!ctx) throw new Error("useQuestionAnswers must be used within a QuestionAnswersProvider");
    return ctx;
};