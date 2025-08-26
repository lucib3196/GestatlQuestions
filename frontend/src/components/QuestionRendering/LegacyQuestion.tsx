// LegacyQuestion.tsx
import { useContext, useEffect, useMemo, useState, useCallback } from "react";
import type { FormEvent } from "react";
import { MathJax } from "better-react-mathjax";

import { SolutionPanel } from "./SolutionPanel";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";

import { getQuestionHTML, getSolutionHTML } from "./utils/fetchLegacy";
import { useAdaptiveParams } from "./utils/useAdaptiveParams";
import { useQuestionMeta } from "./utils/fetchQuestionMetadata";

import { trueish } from "../../utils/truish";
import applyPlaceHolders from "../../utils/flattenParams";
import { processPrairielearnTags } from "../../legacy/readPrairielearn";

import QuestionInfo from "./QuestionInfo";
import {
    SubmitAnswerButton,
    ResetQuestionButton,
    GenerateNewVariantButton,
    ShowSolutionStep,
} from "../Buttons";
import showCorrectAnswer from "./utils/formatCorrectAnswersLegacy";

type ChoiceParams = { fracQuestions: [number, number] };
const CHOICE_PARAMS: ChoiceParams = { fracQuestions: [1.0, 1.0] };

export function LegacyQuestion() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const { codeRunningSettings } = useContext(QuestionSettingsContext);

    const [isSubmitted, setIsSubmitted] = useState(false);
    const [variantLoading, setVariantLoading] = useState(false);
    const [variantError, setVariantError] = useState<string | null>(null);

    const [questionHtml, setQuestionHtml] = useState<string>("");
    const [solutionHTML, setSolutionHTML] = useState<string[]>([]);
    const [showSolution, setShowSolution] = useState<boolean>(false);

    const {
        data: question,
        loading: qLoading,
        error: qError,
        // keepPreviousData behavior recommended in the hook to avoid null-flash
        reset: refetchQmeta,
    } = useQuestionMeta(selectedQuestion);

    const isAdaptive = useMemo(
        () => trueish(question?.isAdaptive),
        [question?.isAdaptive]
    );

    const {
        params,
        loading: pLoading,
        error: pError,
        reset: refetchParams,
    } = useAdaptiveParams(
        selectedQuestion ?? null,
        codeRunningSettings,
        isAdaptive
    );

    // Build HTML + solution when inputs change
    useEffect(() => {
        let ignore = false; // prevent race: only apply latest result

        const run = async () => {
            if (!selectedQuestion) return;
            if (isAdaptive && pLoading) return; // wait for adaptive params

            try {
                const [rawHtml, rawSolution] = await Promise.all([
                    getQuestionHTML(selectedQuestion),
                    getSolutionHTML(selectedQuestion),
                ]);

                // Apply placeholders with current params
                const replacedQ = applyPlaceHolders(rawHtml, params);
                const replacedS = applyPlaceHolders(rawSolution, params);

                const [{ htmlString: qStr }, { solutionsStrings: sStr }] = [
                    processPrairielearnTags(replacedQ, params, "", "", CHOICE_PARAMS),
                    processPrairielearnTags(replacedS, params, "", "", CHOICE_PARAMS),
                ];


                if (!ignore) {
                    setQuestionHtml(qStr);
                    setSolutionHTML(Object.values(sStr ?? {}));
                }
            } catch (err) {
                console.error("Failed to build question HTML/solution:", err);
                if (!ignore) {
                    // Keep old questionHtml to avoid flicker; show inline error
                    setVariantError("Failed to load this question. Please try again.");
                }
            }
        };

        run();
        return () => {
            ignore = true;
        };
        // Only rerun when the actual inputs to HTML change
    }, [selectedQuestion, isAdaptive, pLoading, params]);

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
            // Refresh params (and optionally metadata) without clearing HTML
            await Promise.all([refetchParams()]);
            setIsSubmitted(false);
            setShowSolution(false);
        } catch {
            setVariantError("Variant generation failed. Please try again.");
        } finally {
            setVariantLoading(false);
        }
    }, [refetchParams]);

    // Loading
    if ((qLoading && !question) || (isAdaptive && !params)) {
        return (
            <div className="max-w-5xl mx-auto my-8 px-4">
                <div className="space-y-3">
                    <div className="h-4 w-1/2 rounded bg-slate-200 animate-pulse" />
                    Loading
                    <div className="h-24 w-full rounded bg-slate-200 animate-pulse" />
                </div>
            </div>
        );
    }

    // Error
    if (qError) {
        return (
            <div className="max-w-5xl mx-auto my-8 px-4">
                <div className="rounded-lg border border-red-300 bg-red-50 text-red-800 p-4 shadow-sm">
                    {qError}
                </div>
            </div>
        );
    }

    if (!question) return null;

    return (
        <MathJax>
            <div className="max-w-5xl mx-auto my-8 px-4">
                {/* Main card */}
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm">
                    <div className="p-4">
                        <QuestionInfo qmetadata={question} />

                        {/* Alerts */}
                        <div className="mt-3 space-y-2">
                            {pLoading && (
                                <div
                                    className="rounded-lg border border-blue-200 bg-blue-50 text-blue-900 p-3 text-sm"
                                    aria-live="polite"
                                >
                                    Loading parameters…
                                </div>
                            )}
                            {pError && (
                                <div
                                    className="rounded-lg border border-amber-200 bg-amber-50 text-amber-900 p-3 text-sm"
                                    aria-live="polite"
                                >
                                    Parameters failed to load; showing last known values.
                                </div>
                            )}
                            {variantError && (
                                <div
                                    className="rounded-lg border border-red-200 bg-red-50 text-red-900 p-3 text-sm"
                                    aria-live="polite"
                                >
                                    {variantError}
                                </div>
                            )}
                        </div>

                        {/* Question HTML */}
                        <div
                            className="mt-4 prose max-w-none"
                            dangerouslySetInnerHTML={{ __html: questionHtml }}
                        />

                        {/* Actions */}
                        <div className="mt-6 bg-white border border-slate-200 rounded-xl shadow-sm p-4">
                            <div className="flex flex-wrap items-center gap-3 justify-center">
                                <form onSubmit={handleSubmit}>
                                    <SubmitAnswerButton
                                        disabled={isSubmitted || pLoading || variantLoading}
                                    />
                                </form>

                                <ResetQuestionButton
                                    onClick={handleReset}
                                    disabled={!isSubmitted || variantLoading}
                                />

                                <GenerateNewVariantButton
                                    onClick={handleGenerateVariant}
                                    disabled={variantLoading || pLoading}
                                />

                                <ShowSolutionStep
                                    onClick={() => setShowSolution((prev) => !prev)}
                                    disabled={false}
                                    showSolution={showSolution}
                                />
                            </div>
                        </div>

                        {/* Correct answers (after submit) */}
                        {showCorrectAnswer(isSubmitted, params ?? null)}

                        {/* Solution (toggle) */}
                        {showSolution && (
                            <SolutionPanel solution={solutionHTML}></SolutionPanel>
                        )}
                    </div>
                </div>
            </div>
        </MathJax>
    );
}
