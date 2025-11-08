import {
    useCallback,
    useEffect,
    useMemo,
    useState,
    type FormEvent,
} from "react";
import { QuestionHTMLToReact } from "../QuestionComponents/ParseQuestionHTML";
import { useAdaptiveParams } from "../../api";
import { trueish } from "../../utils";
import { Loading } from "../Base/Loading";
import { ButtonActions } from "./ActionButtons";
import DisplayCorrectAnswer from "./DisplayCorrectAnswer";
import { Error } from "../Generic/Error";
import { QuestionHeader } from "./QuestionHeader";
import { useParsedQuestionHTML } from "../QuestionView/fetchFormattedLegacy";
import { useQuestionContext } from "../../context/QuestionContext";
import { useRawQuestionHTML } from "../QuestionView/fetchFormattedLegacy";

export default function QuestionCard() {
    const { questionMeta: qdata } = useQuestionContext();
    const [loading, setLoading] = useState(false);
    const [formattedQuestion, setFormattedQuestion] = useState<string>("");
    const [formattedSolution, setFormattedSolution] = useState<string | null>("");
    const [isSubmitted, setIsSubmitted] = useState(false);
    const isAdaptive = useMemo(
        () => trueish(qdata?.isAdaptive),
        [qdata?.isAdaptive]
    );
    const { params } = useAdaptiveParams(isAdaptive);
    const { questionHtml, solutionHTML } = useRawQuestionHTML();
    const parsed = useParsedQuestionHTML(
        questionHtml ?? "",
        isAdaptive && params ? params : null,
        solutionHTML ?? ""
    );
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
    let questionPath = qdata?.question_path ?? qdata?.title ?? "";
    questionPath += "/clientFiles";

    if (!qdata) return <Error error={"Failed to get question data"} />;
    if (!formattedQuestion)
        return (
            <Error error="Could not render question. No question.html present." />
        );

    // const generateVariant = useCallback(async () => {
    //     await refetch()
    //     setIsSubmitted(false);
    //     setShowSolution(false);
    // }, [refetch, setShowSolution]);


    return (
        <>
            <QuestionHeader question={qdata} />

            <QuestionHTMLToReact html={formattedQuestion} />
        </>
    );

    // // --- Loading / Error Handling ---

    // if (pError) return <Error error={pError} />;
    // if (!qdata) return <Error error={"Failed to get question data"} />
    // if (!questionHtml)
    //     return <Error error="Could not render question. No question.html present." />;
    // console.log(questionHtml)
    // // --- Main Render ---
    // return (
    //     <>
    //         <QuestionHeader question={qdata} />
    //         {(!params && isAdaptive) ? <Loading /> : <QuestionHTMLToReact html={questionHtml} />}
    //         <div className="w-3/4 flex flex-col items-center">
    //             <ButtonActions
    //                 isSubmitted={isSubmitted}
    //                 showSolution={() => setShowSolution((prev) => !prev)}
    //                 handleSubmit={handleSubmit}
    //                 generateVarient={generateVariant}
    //             />
    //             {isSubmitted && (
    //                 <div className="w-full flex justify-center flex-col items-center mb-10">
    //                     <DisplayCorrectAnswer questionParams={params ?? null} />
    //                 </div>
    //             )}
    //         </div>
    //     </>
    // );
}
