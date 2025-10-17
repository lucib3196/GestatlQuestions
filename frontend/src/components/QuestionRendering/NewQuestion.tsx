import { useContext, useCallback, useEffect } from "react";
import type { FormEvent } from "react";
import { MathJax } from "better-react-mathjax";

import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";
import { trueish } from "../../utils";
import { getQuestionMeta } from "../../api/questionHooks";
import { getAdaptiveParams } from "../../api/questionHooks";
import useQuestionRender from "./utils/useQuestionRender";

import { QuestionPanel } from "./QuestionPanel";
import QuestionInfo from "../Question/QuestionHeader";
import { SolutionPanel } from "../Question/SolutionPanel";
import {
  SubmitAnswerButton,
  ResetQuestionButton,
  GenerateNewVariantButton,
  ShowSolutionStep,
} from "../Generic/Buttons";

import { useState } from "react";

export function NewQuestion() {
  const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
  const { codeRunningSettings } = useContext(QuestionSettingsContext);

  const [isSubmitted, setIsSubmitted] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [variantLoading, setVariantLoading] = useState(false);
  const [variantError, setVariantError] = useState<string | null>(null);

  const {
    data: question,
    loading: qLoading,
    error: qError,
    reset: refetchQmeta,
  } = getQuestionMeta(selectedQuestion);

  const isAdaptive = trueish(question?.isAdaptive);

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

  useEffect(() => {
    setIsSubmitted(false);
    setShowSolution(false);
    setVariantError(null);
  }, [selectedQuestion]);

  const { formattedQuestions, formattedInputs, formattedSolution } =
    useQuestionRender(question ?? null, params, isAdaptive, isSubmitted);

  const handleSubmit = useCallback((e: FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);
  }, []);

  const handleReset = useCallback(() => {
    setIsSubmitted(false);
  }, []);

  const handleGenerateVariant = useCallback(async () => {
    try {
      setVariantLoading(true);
      setVariantError(null);
      // Run in parallel; params refetch will no-op when not adaptive
      await Promise.all([refetchParams()]);
      setIsSubmitted(false);
      setShowSolution(false);
    } catch (e) {
      setVariantError("Variant generation failed");
    } finally {
      setVariantLoading(false);
    }
  }, [refetchQmeta, refetchParams]);

  // Loading / Error states
  if (qLoading) return <div>Loading question…</div>;
  if (qError) {
    return (
      <div className="w-full max-w-3xl mx-auto my-8 p-6 rounded-lg bg-red-100 border border-red-400 text-red-800 font-semibold text-center shadow">
        {qError}
      </div>
    );
  }
  if (!question) return null;

  return (
    <div className="w-full max-w-6xl bg-white shadow-lg p-9 rounded-lg">
      <QuestionInfo qmetadata={question} />

      {/* Adaptive params loading/error */}
      {isAdaptive && (pLoading || variantLoading) && (
        <div className="mt-4">Generating parameters…</div>
      )}
      {isAdaptive && (pError || variantError) && (
        <div className="mt-4 p-4 bg-red-100 text-red-800 rounded">
          {pError ?? "Could not generate question data"}
        </div>
      )}

      {/* Render blocks */}
      {formattedQuestions.map((qStr, idx) => (
        <div key={idx} className="mt-6">
          <MathJax>
            <QuestionPanel
              question={qStr || ""}
              image={question.rendering_data[idx]?.image}
            />
            {formattedInputs[idx]}
            {formattedSolution.length > 0 && showSolution ? (
              <SolutionPanel solution={formattedSolution as React.ReactNode[]} />
            ) : null}
          </MathJax>
        </div>
      ))}

      {/* Actions */}

      <div className="flex justify-end gap-4 mt-6">
        {formattedSolution.length > 0 && (
          <ShowSolutionStep
            onClick={() => setShowSolution((prev) => !prev)}
            disabled={false}
            showSolution={showSolution}
          />
        )}

        <form onSubmit={handleSubmit}>
          <SubmitAnswerButton disabled={isSubmitted} />
        </form>

        <ResetQuestionButton onClick={handleReset} disabled={!isSubmitted} />

        <GenerateNewVariantButton
          onClick={handleGenerateVariant}
          disabled={variantLoading}
        />
      </div>
    </div>
  );
}
