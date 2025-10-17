import React, { createContext, useContext, useState } from "react";

type QuestionSelectionContextType = {
    questionID: string | null;
    setQuestionID: React.Dispatch<React.SetStateAction<string | null>>;
};

export const QuestionSelectionContext =
    createContext<QuestionSelectionContextType>({
        questionID: null,
        setQuestionID: () => { },
    });

const QuestionSelectionProvider = ({
    children,
}: {
    children: React.ReactNode;
}) => {
    const [questionID, setQuestionID] = useState<string | null>(null);
    return (
        <QuestionSelectionContext.Provider
            value={{
                questionID,
                setQuestionID,
            }}
        >
            {children}
        </QuestionSelectionContext.Provider>
    );
};


export function useQuestion() {
    const context = useContext(QuestionSelectionContext);
    if (context === undefined) {
        throw new Error("useQuestion must be used within an QuestionSelectionProvider")
    }
    return context;
}
export default QuestionSelectionProvider;
