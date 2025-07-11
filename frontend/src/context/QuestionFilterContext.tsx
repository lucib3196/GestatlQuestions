import React, { createContext, useState } from 'react';

type QuestionFilterContextType = {
    showAllQuestions: boolean;
    setShowAllQuestions: React.Dispatch<React.SetStateAction<boolean>>;
    isAdaptive: string | boolean;
    setIsAdaptive: React.Dispatch<React.SetStateAction<string | boolean>>;
};

export const QuestionFilterContext = createContext<QuestionFilterContextType>({
    showAllQuestions: false,
    setShowAllQuestions: () => { },
    isAdaptive: "false",
    setIsAdaptive: () => { },
});

const QuestionProvider = ({ children }: { children: React.ReactNode }) => {
    const [isAdaptive, setIsAdaptive] = useState<string | boolean>("false");
    const [showAllQuestions, setShowAllQuestions] = useState<boolean>(false);

    return (
        <QuestionFilterContext.Provider
            value={{ isAdaptive, setIsAdaptive, showAllQuestions, setShowAllQuestions }}
        >
            {children}
        </QuestionFilterContext.Provider>
    );
};

export default QuestionProvider;
