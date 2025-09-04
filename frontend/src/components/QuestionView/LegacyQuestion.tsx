// React & Types
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

// External libraries
import { MathJax } from "better-react-mathjax";

// Context
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";

// API
import { getAdaptiveParams, getQuestionMeta } from "../../api/questionHooks";

// Utils
import { trueish } from "../../utils";

// Components
import QuestionInfo from "./QuestionInfo";
import { SolutionPanel } from "./SolutionPanel";
import showCorrectAnswer from "../QuestionRendering/utils/formatCorrectAnswersLegacy";
import { Loading } from "../Generic/Loading";
import { Error } from "../Generic/Error";
import Alerts from "./QuestionAlerts";
import ActionBar from "./LegacyActionBar";

// Local hooks
import { useFormattedLegacy } from "./fetchFormattedLegacy";


const QuestionHtml: React.FC<{ html: string }> = ({ html }) => (
    <div className="mt-4 prose max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
);

export function LegacyQuestion() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const { codeRunningSettings } = useContext(QuestionSettingsContext);

    const [isSubmitted, setIsSubmitted] = useState(false);
    const [variantLoading, setVariantLoading] = useState(false);
    const [variantError, setVariantError] = useState<string | null>(null);
    const [showSolution, setShowSolution] = useState<boolean>(false);

    const {
        data: question,
        loading: qLoading,
        error: qError,
    } = getQuestionMeta(selectedQuestion);

    const isAdaptive = useMemo(() => trueish(question?.isAdaptive), [question?.isAdaptive]);
    const {
        params,
        loading: pLoading,
        error: pError,
        reset: refetchParams,
    } = getAdaptiveParams(selectedQuestion ?? null, codeRunningSettings, isAdaptive);

    const { questionHtml, solutionHTML } = useFormattedLegacy(selectedQuestion ?? null, params);

    // Reset transient UI when switching questions
    useEffect(() => {
        setIsSubmitted(false);
        setVariantError(null);
        setShowSolution(false);
    }, [selectedQuestion]);

    // Handlers
    const handleSubmit = useCallback((e: FormEvent) => {
        e.preventDefault();
        setIsSubmitted(true);
    }, []);

    const handleReset = useCallback(() => setIsSubmitted(false), []);

    const handleGenerateVariant = useCallback(async () => {
        try {
            setVariantLoading(true);
            setVariantError(null);
            await refetchParams();
            setIsSubmitted(false);
            setShowSolution(false);
        } catch {
            setVariantError("Variant generation failed. Please try again.");
        } finally {
            setVariantLoading(false);
        }
    }, [refetchParams]);

    /* ----------------------------- States ----------------------------- */

    if ((qLoading && !question) || (isAdaptive && !params)) return <Loading />;
    if (!questionHtml) return <Error error={"Could not render question no question.html present"} />
    if (qError) return <Error error={qError as string} />;
    if (!question) return null;

    return (
        <MathJax>
            <div className="max-w-5xl mx-auto my-8 px-4">
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm">
                    <div className="p-4">
                        <QuestionInfo qmetadata={question} />

                        <Alerts pLoading={pLoading} pError={pError as string | null} variantError={variantError} />

                        <QuestionHtml html={questionHtml} />

                        <ActionBar
                            onSubmit={handleSubmit}
                            onReset={handleReset}
                            onVariant={handleGenerateVariant}
                            onToggleSolution={() => setShowSolution((s) => !s)}
                            disabledSubmit={isSubmitted || pLoading || variantLoading}
                            disabledReset={!isSubmitted || variantLoading}
                            disabledVariant={variantLoading || pLoading}
                            showSolution={showSolution}
                        />
                        {/* Correct answers (after submit) */}
                        {showCorrectAnswer(isSubmitted, params ?? null)}

                        {/* Solution (toggle) */}
                        {showSolution && <SolutionPanel solution={solutionHTML} />}
                    </div>
                </div>
            </div>
        </MathJax>
    );
}