// NewQuestion.tsx
import { useEffect, useState, useCallback, useContext } from "react";
import type { FormEvent, ReactNode } from "react";
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
import { MathJax } from "better-react-mathjax";

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


export function NewQuestion() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const { codeRunningSettings } = useContext(QuestionSettingsContext);

    const [question, setQuestion] = useState<QuestionMetadata | null>(null);
    const [params, setParams] = useState<QuestionParams | null>(null);
    const [formattedQuestion, setFormattedQuestion] = useState<string[]>([]);
    const [formattedInputs, setFormattedInputs] = useState<ReactNode[] | null>(
        null
    );
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, SetError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const roundValues = true;

    const handleError = useCallback((msg: string, err?: unknown) => {
        console.error(msg, err);
        SetError(true),
            setErrorMessage(msg);
    }, [])

    // Fetch the question 
    useEffect(() => {
        if (!selectedQuestion) return;
        const controller = new AbortController();

        // Reset all the states when question changes
        SetError(false);
        setErrorMessage("");
        setIsSubmitted(false);
        setQuestion(null);
        setParams(null);
        setFormattedQuestion([]);
        setFormattedInputs([]);

        (async () => {
            try {
                const response = await api.get(
                    `/local_questions/get_question_newformat/${selectedQuestion}`
                );
                const qData: QuestionMetadata =
                    typeof response.data === "string"
                        ? JSON.parse(response.data)
                        : response.data;
                setQuestion(qData);
            } catch (e: any) {
                if (e.name === "CanceledError") return;
                handleError("Could not get question data", e);
            }
        })();
        return () => controller.abort();
    }, [selectedQuestion, handleError])

    // Get the paras if the question is adaptive

    useEffect(() => {
        const isAdaptive = question && (question.isAdaptive === true || question.isAdaptive === "true");
        if (!isAdaptive) return;
        const controller = new AbortController();

        (async () => {
            try {
                const res = await api.get(
                    `/local_questions/get_server_data/${encodeURIComponent(selectedQuestion)}/${encodeURIComponent(codeRunningSettings)}`,
                    { signal: controller.signal }
                );
                const pData = res.data?.quiz_response ?? null;

                if (pData == null) {
                    const raw = res.data?.error;
                    const msg = typeof raw === "object" ? JSON.stringify(raw) : String(raw ?? "Unknown error");
                    handleError(msg);
                    return;
                }
                setParams(pData);
            } catch (e: any) {
                if (e.name === "CanceledError") return;
                handleError("Could not generate question data", e);
            }
        })();

        return () => controller.abort();


    }, [question, selectedQuestion, codeRunningSettings, handleError])


    useEffect(() => {
        if (!question) return;

        // Make a copy to preven overwritting 
        const clonedRenderingData = question.rendering_data.map(r => ({
            ...r,
            questionInputs: r.questionInputs.map(inp => ({ ...inp }))
        }))

        // Where to store 
        const qStrings: string[] = [];
        const inputs: ReactNode[] = [];

        const isAdaptive = question && (question.isAdaptive === true || question.isAdaptive === "true");
        if (!isAdaptive) {
            clonedRenderingData.forEach(rd => {
                qStrings.push(rd.question_template);
                console.log(rd.questionInputs)
            });
            setFormattedQuestion(qStrings)
            setFormattedInputs([])
            return
        }

        if (!params) return;

        // update Inputs 
        clonedRenderingData.forEach(rd => {
            rd.questionInputs.forEach(input => {
                if (input.qtype === "number" && typeof input.units === "string") {
                    input.units = formatTemplateWithParams(input.units, params)
                }
            })
        })



        clonedRenderingData.forEach(rd => {
            qStrings.push(formatTemplateWithParams(rd.question_template, params, roundValues));
            inputs.push(
                renderQuestionInputs(rd.questionInputs, params.correct_answers, isSubmitted)
            );
        });

        setFormattedQuestion(qStrings);
        setFormattedInputs(inputs);

    }, [question, params, selectedQuestion, isSubmitted])

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

    function format() {
        if (!formattedQuestion || !formattedInputs || !question) return null;
        return formattedQuestion.map((formattedQ, idx) => (
            <>
                <MathJax>
                    <QuestionPanel
                        key={idx}
                        question={formattedQ || ""}
                        image={question.rendering_data[idx]?.image}
                    />
                    {formattedInputs[idx]}
                </MathJax>
            </>
        ));
    }

    if (error === true) {
        return (
            <div className="w-full max-w-3xl mx-auto my-8 p-6 rounded-lg bg-red-100 border border-red-400 text-red-800 font-semibold text-center shadow">
                {errorMessage}
            </div>
        );
    }

    return (
        <div className="w-full max-w-6xl bg-white shadow-lg p-9 rounded-lg">
            <QuestionInfo qmetadata={question} />
            {format()}
            <form onSubmit={handleSubmit}>
                <div className="flex justify-end gap-4 mt-6">
                    <SubmitAnswerButton
                        disabled={isSubmitted}
                        onClick={() => handleSubmit}
                    />
                    <ResetQuestionButton onClick={handleReset} disabled={!isSubmitted} />
                    <GenerateNewVariantButton
                        onClick={handleGenerateVariant}
                        disabled={false}
                    />
                </div>
            </form>
        </div>
    );
}
