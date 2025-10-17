import {
    useState,
    useCallback,
    useContext,
    useMemo,
    type FormEvent,
} from "react";

import Panel from "../components/Base/Panel";
import { ButtonActions } from "../components/Question/ActionButtons";
import SectionContainer from "../components/Base/SectionContainer";
import { SolutionPanel } from "../components/Question/SolutionPanel";
import { QuestionHeader } from "../components/Question/QuestionHeader";
import { QuestionHtml } from "../components/Question/QuestionHtml";
import { Loading } from "../components/Base/Loading";
import { QuestionSettingsContext } from "../context/GeneralSettingsContext";
import { Error } from "../components/Generic/Error";
import { getQuestionMeta, getAdaptiveParams } from "../api";
import { useFormattedLegacy } from "../components/QuestionView/fetchFormattedLegacy";
import DeveloperOptions from "../components/Question/DeveloperOptions";
import {
    Panel as RPanel,
    PanelGroup,
    PanelResizeHandle,
} from "react-resizable-panels";
import { trueish } from "../utils";
import DisplayCorrectAnswer from "../components/Question/DisplayCorrectAnswer";

type SolutionProps = {
    solution?: string[] | null;
};
export function SolutionResizable({ solution }: SolutionProps) {
    return (
        <>
            <RPanel id="solution-panel" order={1} defaultSize={40} minSize={10}>
                <Panel>{<SolutionPanel solution={solution ?? []} />}</Panel>
            </RPanel>
        </>
    );
}



// --- Main Question View ---
export function QuestionView() {
    const selectedQuestion = "9a317750-6a20-4cfe-aeb5-93f54dccb77a";
    const { codeRunningSettings } = useContext(QuestionSettingsContext);
    const [showSolution, setShowSolution] = useState<boolean>(false);
    const [isSubmitted, setIsSubmitted] = useState(false);


    // Question metadata
    const {
        data: qdata,
        loading: qLoading,
        error: qError,
    } = getQuestionMeta(selectedQuestion);

    const isAdaptive = useMemo(
        () => trueish(qdata?.isAdaptive),
        [qdata?.isAdaptive]
    );

    // Adaptive parameters
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

    // Legacy formatted HTML
    const { questionHtml, solutionHTML } = useFormattedLegacy(
        selectedQuestion ?? null,
        params,
        questionTitle
    );

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
        <SectionContainer id={"questionView"} style="hero">
            <PanelGroup autoSaveId="conditional" direction="horizontal">
                {showSolution && <SolutionResizable solution={solutionHTML} />}
                <PanelResizeHandle />
                <RPanel id="question-view" order={2} defaultSize={40} minSize={30}>
                    <Panel className="">
                        <QuestionHeader question={qdata} />
                        <DeveloperOptions />

                        <QuestionHtml html={questionHtml ?? ""} />
                        <ButtonActions
                            isSubmitted={isSubmitted}
                            showSolution={() => setShowSolution((prev) => !prev)}
                            handleSubmit={handleSubmit}
                            generateVarient={generateVarient}
                        />
                        {isSubmitted && (
                            <div className="w-full  flex justify-center flex-col items-center mb-10">
                                <DisplayCorrectAnswer
                                    questionParams={params ?? null}
                                ></DisplayCorrectAnswer>
                            </div>
                        )}
                    </Panel>
                </RPanel>
            </PanelGroup>

        </SectionContainer>
    );
}
