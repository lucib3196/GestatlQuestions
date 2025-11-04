import {
    useCallback,
    useMemo,
    useState,
    type FormEvent,
} from "react";

import { useAdaptiveParams } from "../../api";
import { trueish } from "../../utils";
import { useSelectedQuestion } from "../../context/SelectedQuestionContext";
import { Loading } from "../Base/Loading";
import { ButtonActions } from "./ActionButtons";
import DisplayCorrectAnswer from "./DisplayCorrectAnswer";
import { Error } from "../Generic/Error";
import { QuestionHeader } from "./QuestionHeader";
import { QuestionHtml } from "./QuestionHtml";
import { useFormattedLegacy } from "../QuestionView/fetchFormattedLegacy";

type QuestionCardProps = {
    setShowSolution: React.Dispatch<React.SetStateAction<boolean>>;
    setSolution: React.Dispatch<React.SetStateAction<string[] | null>>;
};

export default function QuestionCard({
    setShowSolution,
    setSolution,
}: QuestionCardProps) {
    const { questionMeta: qdata } = useSelectedQuestion();

    const [isSubmitted, setIsSubmitted] = useState(false);
    const isAdaptive = useMemo(() => trueish(qdata?.isAdaptive), [qdata?.isAdaptive]);

    const {
        params,
        loading: pLoading,
        error: pError,
        refetch
    } = useAdaptiveParams(isAdaptive);

    const questionTitle = qdata?.title ?? "Untitled Question";

    const {
        questionHtml,
        solutionHTML,
        loading: qLoading,
    } = useFormattedLegacy(params, questionTitle);

    useMemo(() => {
        if (solutionHTML) setSolution(solutionHTML);
    }, [solutionHTML, setSolution]);

    const handleSubmit = useCallback((e: FormEvent) => {
        e.preventDefault();
        setIsSubmitted(true);
    }, []);

    const generateVariant = useCallback(async () => {
        await refetch()
        setIsSubmitted(false);
        setShowSolution(false);
    }, [refetch, setShowSolution]);

    // --- Loading / Error Handling ---
    if (pLoading || qLoading) return <Loading />;
    if (pError) return <Error error={pError} />;
    if (!qdata) return <Error error={"Failed to get question data"} />
    if (!questionHtml)
        return <Error error="Could not render question. No question.html present." />;

    // --- Main Render ---
    return (
        <>
            <QuestionHeader question={qdata} />
            {(!params && isAdaptive) ? <Loading /> : <QuestionHtml html={questionHtml} />}
            <div className="w-3/4 flex flex-col items-center">
                <ButtonActions
                    isSubmitted={isSubmitted}
                    showSolution={() => setShowSolution((prev) => !prev)}
                    handleSubmit={handleSubmit}
                    generateVarient={generateVariant}
                />
                {isSubmitted && (
                    <div className="w-full flex justify-center flex-col items-center mb-10">
                        <DisplayCorrectAnswer questionParams={params ?? null} />
                    </div>
                )}
            </div>
        </>
    );
}