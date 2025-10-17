import {
    useState,
    useCallback,
    useContext,
    useMemo,
    type FormEvent,
} from "react";

import { Loading } from "../Base/Loading";
import { Error } from "../Generic/Error";
import { getQuestionMeta } from "../../api";
import { useFormattedLegacy } from "../QuestionView/fetchFormattedLegacy";
import { trueish } from "../../utils";
import { QuestionSettingsContext } from "./../../context/GeneralSettingsContext";
import { getAdaptiveParams } from "../../api";
import { QuestionHtml } from "./QuestionHtml";
import { ButtonActions } from "./ActionButtons";
import DisplayCorrectAnswer from "./DisplayCorrectAnswer";
import { QuestionHeader } from "./QuestionHeader";
import { useQuestion } from "../../context/QuestionSelectionContext";


type QuestionCardProps = {
    setShowSolution: React.Dispatch<React.SetStateAction<boolean>>;
    setSolution: React.Dispatch<React.SetStateAction<string[] | null>>;
};

export default function QuestionCard({
    setShowSolution,
    setSolution,
}: QuestionCardProps) {
    const { questionID: selectedQuestion } = useQuestion()
    const { codeRunningSettings } = useContext(QuestionSettingsContext);
    const [isSubmitted, setIsSubmitted] = useState(false);

    const {
        data: qdata,
        loading: qLoading,
        error: qError,
    } = getQuestionMeta(selectedQuestion);
    const isAdaptive = useMemo(
        () => trueish(qdata?.isAdaptive),
        [qdata?.isAdaptive]
    );
    // Get Question Parameters
    const {
        params,
        loading: pLoading,
        error: pError,
        reset: refetchParams,
    } = getAdaptiveParams(
        selectedQuestion ?? null,
        codeRunningSettings,
        isAdaptive
    );

    const handleSubmit = useCallback((e: FormEvent) => {
        e.preventDefault();
        setIsSubmitted(true);
    }, []);

    const questionTitle = qdata?.title;

    const { questionHtml, solutionHTML } = useFormattedLegacy(
        selectedQuestion ?? null,
        params,
        questionTitle
    );
    setSolution(solutionHTML);

    const generateVarient = useCallback(async () => {
        await refetchParams();
        setIsSubmitted(false);
        setShowSolution(false);
    }, [refetchParams]);

    if (qLoading || pLoading || !qdata) return <Loading />;
    if (qError || pError) {
        return <Error error={(qError ?? pError) as string} />;
    }
    if (!questionHtml)
        return (
            <Error error={"Could not render question no question.html present"} />
        );
    return (
        <>
            <QuestionHeader question={qdata} />
            <QuestionHtml html={questionHtml} />
            <div className="w-3/4 flex flex-col items-center">
                <ButtonActions
                    isSubmitted={isSubmitted}
                    showSolution={() => setShowSolution(prev => !prev)}
                    handleSubmit={handleSubmit}
                    generateVarient={generateVarient}
                />
                {isSubmitted && (
                    <div className="w-full flex justify-center flex-col items-center mb-10">
                        <DisplayCorrectAnswer
                            questionParams={params ?? null}
                        ></DisplayCorrectAnswer>
                    </div>
                )}
            </div>
        </>
    );
}


