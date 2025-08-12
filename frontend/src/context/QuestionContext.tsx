import React, { createContext, useState } from "react"


type RenderingType = "legacy" | "new";
type CodeRunningType = "javascript" | "python";

type QuestionContextValue = {
    // Filters
    title: string;
    setTitle: React.Dispatch<React.SetStateAction<string>>;
    qtype: string[];
    setQType: React.Dispatch<React.SetStateAction<string[]>>;
    topic: string[];
    setTopic: React.Dispatch<React.SetStateAction<string[]>>;
    isAdaptive: boolean; // ← boolean only
    setIsAdaptive: React.Dispatch<React.SetStateAction<boolean>>;
    createdBy: string;
    setCreatedBy: React.Dispatch<React.SetStateAction<string>>;

    // Settings
    showAllQuestions: boolean;
    setShowAllQuestions: React.Dispatch<React.SetStateAction<boolean>>;
    renderingSettings: RenderingType;
    setRenderingSettings: React.Dispatch<React.SetStateAction<RenderingType>>;
    codeRunningSettings: CodeRunningType;
    setCodeRunningSettings: React.Dispatch<React.SetStateAction<CodeRunningType>>;
};

// Safer: undefined until provider sets it
export const QuestionContext = createContext<QuestionContextValue | undefined>(undefined);

type ProviderProps = { children: React.ReactNode };

export const QuestionDBProvider = ({ children }: ProviderProps) => {
    // Filters
    const [title, setTitle] = useState("");
    const [qtype, setQType] = useState<string[]>([]);
    const [topic, setTopic] = useState<string[]>([]);
    const [isAdaptive, setIsAdaptive] = useState<boolean>(false);
    const [createdBy, setCreatedBy] = useState("");
    const [showAllQuestions, setShowAllQuestions] = useState(false);

    // Settings
    const [renderingSettings, setRenderingSettings] = useState<RenderingType>("new");
    const [codeRunningSettings, setCodeRunningSettings] = useState<CodeRunningType>("javascript");

    const value = React.useMemo(
        () => ({
            title, setTitle,
            qtype, setQType,
            topic, setTopic,
            isAdaptive, setIsAdaptive,
            createdBy, setCreatedBy,
            showAllQuestions, setShowAllQuestions,
            renderingSettings, setRenderingSettings,
            codeRunningSettings, setCodeRunningSettings,
        }),
        [
            title, qtype, topic,
            isAdaptive, createdBy,
            showAllQuestions,            // ← add this!
            renderingSettings, codeRunningSettings,
        ]
    );

    return <QuestionContext.Provider value={value}>{children}</QuestionContext.Provider>;
};

export const useQuestionContext = () => {
    const ctx = React.useContext(QuestionContext);
    if (!ctx) throw new Error("useQuestionContext must be used within <QuestionDBProvider>");
    return ctx;
};
