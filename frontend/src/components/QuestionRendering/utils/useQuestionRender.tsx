import { useMemo, type ReactNode } from "react";

import type {
  QuestionMetadata,
  QuestionParams,
  QuestionInput,
} from "../../../types/types";



import { MultipleChoiceInput } from "../MultipleChoiceInput";
import NumberInputDynamic from "../QuestionInputs/NumberInput";
import applyPlaceHolders from '../../../utils/flattenParams';


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

export default function useQuestionRender(
  question: QuestionMetadata | null,
  params: QuestionParams | null,
  isAdaptive: boolean,
  isSubmitted: boolean
) {
  return useMemo(() => {
    if (!question) {
      return {
        formattedQuestions: [] as string[],
        formattedInputs: [] as ReactNode[],
        formattedSolution: [] as string[] | ReactNode[] | Element[],
      };
    }

    const rd = question.rendering_data.map((r) => ({
      ...r,
      questionInputs: r.questionInputs.map((inp) => ({ ...inp })),
    }));

    const qStrings: string[] = [];
    const inputs: ReactNode[] = [];
    const solutionHints: ReactNode[] = [];

    // Todo possibly add solution guides to non adaptive questions
    if (!isAdaptive) {
      rd.forEach((r) => {
        qStrings.push(r.question_template);
        inputs.push(renderQuestionInputs(r.questionInputs, {}, isSubmitted));
      });
      return {
        formattedQuestions: qStrings,
        formattedInputs: inputs,
        formattedSolution: [],
      };
    }

    if (!params) {
      return {
        formattedQuestions: [],
        formattedInputs: [],
        formattedSolution: [],
      };
    }

    rd.forEach((r) => {
      r.questionInputs.forEach((inp) => {
        if (inp.qtype === "number") {
          if (typeof inp.units === "string")
            inp.units = applyPlaceHolders(inp.units, params);
          if (typeof inp.label === "string")
            inp.label = applyPlaceHolders(inp.label, params);
        }
      });
    });

    rd.forEach((r) => {
      qStrings.push(applyPlaceHolders(r.question_template, params));
      inputs.push(
        renderQuestionInputs(
          r.questionInputs,
          params.correct_answers,
          isSubmitted
        )
      );
      r.solution_render?.solution_hint?.forEach((h) => {
        solutionHints.push(applyPlaceHolders(h, params));
      });
    });

    return {
      formattedQuestions: qStrings,
      formattedInputs: inputs,
      formattedSolution: solutionHints,
    };
  }, [question, params, isAdaptive, isSubmitted]);
}
