// NewQuestion.tsx
import { useEffect, useState, useCallback, useContext, } from "react";
import type { FormEvent, ReactNode } from "react"
import api from "../../api";
import type { QuestionMetadata, QuestionParams } from "../../types/types";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";
import { QuestionInfo } from "./QuestionPanel";
import { QuestionPanel } from "./QuestionPanel";
import {
    SubmitAnswerButton,
    ResetQuestionButton,
    GenerateNewVariantButton,
} from "../Buttons";
import formatTemplateWithParams from "./../../utils/formatQuestion";
import { NumberInputDynamic } from "./NumberInput";
import { MultipleChoiceInput } from "./MultipleChoiceInput";
import type { QuestionInput } from "../../types/types";


function renderQuestionInputs(
    inputs: QuestionInput[],
    correctAnswers: Record<string, any>,
    isSubmitted: boolean
) {
    return inputs.map((value) => {
        switch (value.qtype) {
            case "number":
                return (
                    <NumberInputDynamic
                        key={value.name}
                        inputData={value}
                        correctAnswers={correctAnswers[value.name]}
                        isSubmitted={isSubmitted}
                    />
                );

            case "multiple_choice":
                return (
                    <MultipleChoiceInput
                        key={value.name}
                        {...value}
                        isSubmitted={isSubmitted}
                        shuffle={true}
                    />
                );

            case "checkbox":
                return null;

            default:
                return null;
        }
    });
}

/**
 * Renders new-format question with interactive inputs.
 */
export function NewQuestion() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const { codeRunningSettings } = useContext(QuestionSettingsContext);

    const [question, setQuestion] = useState<QuestionMetadata | null>(null);
    const [params, setParams] = useState<QuestionParams | null>(null);
    const [formattedQuestion, setFormattedQuestion] = useState<string>("");
    const [formattedInputs, setFormattedInputs] = useState<ReactNode>(null);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const roundValues = true;

    // Load question & initial params
    useEffect(() => {
        if (!selectedQuestion) return;

        (async () => {
            try {
                const [qr, pr] = await Promise.all([
                    api.get(`/local_questions/get_question_newformat/${selectedQuestion}`),
                    api.get(`/local_questions/get_server_data/${selectedQuestion}/${codeRunningSettings}`),
                ]);

                const qData: QuestionMetadata =
                    typeof qr.data === "string" ? JSON.parse(qr.data) : qr.data;
                const pData = pr.data.quiz_response;

                setQuestion(qData);
                setParams(pData);
                setIsSubmitted(false);
            } catch (err) {
                console.error("Failed loading new question", err);
            }
        })();
    }, [selectedQuestion, codeRunningSettings]);

    // Format question and inputs when data or submission state changes
    useEffect(() => {
        if (!question || !params) return;

        // update units if necessary
        question.questionInputs.forEach((input) => {
            if (input.qtype === "number" && typeof input.units === "string") {
                input.units = formatTemplateWithParams(input.units, params);
            }
        });

        setFormattedQuestion(
            formatTemplateWithParams(question.question_template, params, roundValues)
        );
        setFormattedInputs(
            renderQuestionInputs(question.questionInputs, params.correct_answers, isSubmitted)
        );
    }, [question, params, isSubmitted]);

    const handleSubmit = useCallback((e: FormEvent) => {
        e.preventDefault();
        setIsSubmitted(true);
    }, []);

    const handleReset = useCallback(() => {
        setIsSubmitted(false);
    }, []);

    const handleGenerateVariant = useCallback(async () => {
        if (!selectedQuestion) return;

        try {
            const { data } = await api.get(
                `/local_questions/get_server_data/${selectedQuestion}/${codeRunningSettings}`
            );
            setParams(data.quiz_response);
            setIsSubmitted(false);
        } catch (err) {
            console.error("Variant generation failed", err);
        }
    }, [selectedQuestion, codeRunningSettings]);

    if (!question) {
        return <div>Loading question…</div>;
    }

    return (
        <div className="w-full max-w-6xl bg-white shadow-lg p-9 rounded-lg">
            <QuestionInfo qmetadata={question} />

            {/* Only render panel when we have at least an empty string */}
            <QuestionPanel question={formattedQuestion || ""} image={question.image} />

            <form onSubmit={handleSubmit}>
                {formattedInputs}

                <div className="flex justify-end gap-4 mt-6">
                    <SubmitAnswerButton disabled={isSubmitted} onClick={() => handleSubmit} />
                    <ResetQuestionButton onClick={handleReset} disabled={!isSubmitted} />
                    <GenerateNewVariantButton onClick={handleGenerateVariant} disabled={false} />
                </div>
            </form>
        </div>
    );
}
