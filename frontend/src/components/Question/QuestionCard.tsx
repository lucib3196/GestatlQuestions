import {
    useState,
    useCallback,
    useContext,
    useMemo,
    type FormEvent,
} from "react";
import SectionContainer from "../Base/SectionContainer";

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
import {
    Panel as RPanel,
    PanelGroup,
    PanelResizeHandle,
} from "react-resizable-panels";
import { SolutionPanel } from "./SolutionPanel";


type QuestionCardProps = {
    setShowSolution: React.Dispatch<React.SetStateAction<boolean>>;
    setSolution: React.Dispatch<React.SetStateAction<string[] | null>>;
};

export default function QuestionCard({
    setShowSolution,
    setSolution,
}: QuestionCardProps) {
    const selectedQuestion = "24685412-60c5-4c69-8bc6-483c061745a8";
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


export function ResizableQuestionContainer() {
    const [showSolution, setShowSolution] = useState(false);
    const [solution, setSolution] = useState<string[] | null>(null);

    return (
        <SectionContainer
            id="questionView"
            style="primary"
            className="relative flex flex-col w-full h-full p-4 sm:p-6 bg-gray-50 dark:bg-gray-900 rounded-2xl shadow-md border border-gray-200 dark:border-gray-700"
        >
            <PanelGroup
                className="flex w-full max-h-4/10 rounded-lg overflow-hidden border border-gray-300 dark:border-gray-700"
                autoSaveId="conditional"
                direction="horizontal"
            >
                {/* Left Solution Panel */}
                {showSolution && (
                    <RPanel
                        id="solution-panel"
                        order={1}
                        defaultSize={50}
                        minSize={25}
                        className="bg-white dark:bg-gray-800 border-r border-gray-300 dark:border-gray-700 p-4 overflow-auto"
                    >
                        <SolutionPanel solution={solution ?? []} />
                    </RPanel>
                )}

                {/* Resize Handle */}
                <PanelResizeHandle className="w-3 cursor-col-resize bg-blue-100 hover:bg-blue-400 dark:bg-blue-700 dark:hover:bg-blue-600 transition-all rounded-sm" />

                {/* Right Question Panel */}
                <RPanel
                    id="question-view"
                    order={2}
                    defaultSize={50}
                    minSize={30}
                    className="flex flex-col items-center justify-center bg-white dark:bg-gray-800 p-6"
                >
                    <QuestionCard setShowSolution={setShowSolution} setSolution={setSolution} />
                </RPanel>
            </PanelGroup>
        </SectionContainer>
    );
}