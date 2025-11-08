import { useEffect, useMemo, useState } from "react";

import { useAdaptiveParams } from "../../api";
import { trueish } from "../../utils";

import { useQuestionAnswers } from "../../context/QuestionAnswerContext";
import { useQuestionContext } from "../../context/QuestionContext";

import { useRawQuestionHTML, useParsedQuestionHTML } from "../QuestionView/fetchFormattedLegacy";
import QuestionHTMLToReact from "../QuestionComponents/ParseQuestionHTML";
import { QuestionHeader } from "../Question/QuestionHeader";
import { Error } from "../Generic/Error";



export default function QuestionEngine() {
    const [formattedQuestion, setFormattedQuestion] = useState<string>("");
    const [formattedSolution, setFormattedSolution] = useState<string | null>("");
    const { questionMeta: qdata } = useQuestionContext();

    const { answers } = useQuestionAnswers();

    const isAdaptive = useMemo(
        () => trueish(qdata?.isAdaptive),
        [qdata?.isAdaptive]
    );

    // Fetch adaptive params if question is adaptive
    const { params } = useAdaptiveParams(isAdaptive);
    // Fetch the raw html what the user edits
    const { questionHtml, solutionHTML } = useRawQuestionHTML();
    // Replaces parameters in the html files, if no paras then just return the string again
    const parsed = useParsedQuestionHTML(
        questionHtml ?? "",
        isAdaptive && params ? params : null,
        solutionHTML ?? ""
    );

    console.log("Current answers", answers)


    useEffect(() => {
        if (parsed) {
            const { qHTML, sHTML } = parsed;
            setFormattedQuestion(qHTML);
            setFormattedSolution(sHTML);
        } else {
            setFormattedQuestion(questionHtml ?? "");
            setFormattedSolution(solutionHTML ?? "");
        }
    }, [parsed, questionHtml, solutionHTML, qdata]);

    if (!qdata) return <Error error={"Failed to get question data"} />;
    return (
        <>
            <QuestionHeader question={qdata} />

            <QuestionHTMLToReact html={formattedQuestion} />

        </>
    );
}
