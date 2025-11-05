import type { QuestionParams } from "../../types/types";
import applyPlaceHolders from "../../utils/flattenParams";
import { useState, useEffect, useCallback} from "react";
import { QuestionAPI } from "../../api/questionCrud";
import { useQuestionContext } from "../../context/QuestionContext";

type FormattedResult = { qStr: string | null; sStr: string[] | null };


function formatWithParams(
    rawHtml: string | null,
    rawSolution: string | null| string[],
    params: QuestionParams | null,
    questionTitle: string
): FormattedResult {
    type ChoiceParams = { fracQuestions: [number, number] };
    const CHOICE_PARAMS: ChoiceParams = { fracQuestions: [1.0, 1.0] };

    if (!rawHtml && !rawSolution) return { qStr: null, sStr: null };

    const replacedQ = rawHtml ? applyPlaceHolders(rawHtml, params) : null;
    const replacedS = rawSolution ? applyPlaceHolders(rawSolution??"", params) : null;

    // const qRes = replacedQ
    //     ? processPrairielearnTags(replacedQ, params, questionTitle, CHOICE_PARAMS)
    //     : undefined;

    const qStr = qRes?.htmlString ?? null;

    // const sRes = replacedS
    //     ? processPrairielearnTags(replacedS, params, questionTitle, CHOICE_PARAMS)
    //     : undefined;

    const solutionsStrings = sRes?.solutionsStrings ?? null;
    const sStr = solutionsStrings ? Object.values(solutionsStrings) : [];

    return { qStr, sStr };
}

// --- React hook ---
export function useFormattedLegacy(params: QuestionParams | null, questionTitle: string) {
    const { selectedQuestionID } = useQuestionContext();

    const [questionHtml, setQuestionHtml] = useState<string | null>(null);
    const [solutionHTML, setSolutionHTML] = useState<string[] | null | string>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);



    const fetchBaseFiles = useCallback(async () => {
        if (!selectedQuestionID) return;
        setLoading(true);
        try {
            const [rawHtmlRes, rawSolutionRes] = await Promise.all([
                QuestionAPI.getQuestionFile(selectedQuestionID, "question.html"),
                QuestionAPI.getQuestionFile(selectedQuestionID, "solution.html"),
            ]);

            setQuestionHtml(rawHtmlRes?.data ?? null);
            setSolutionHTML(rawSolutionRes?.data ?? null);
        } catch (err: any) {
            console.error("❌ Failed to fetch base HTML files:", err);
            setError(err.message || "Failed to fetch base HTML files");
        } finally {
            setLoading(false);
        }
    }, [selectedQuestionID]);

    // Fetch HTML once when question changes
    useEffect(() => {
        fetchBaseFiles();
    }, [fetchBaseFiles]);

    // Re-render processed HTML when params arrive
    useEffect(() => {
        if (!params) return;

        setLoading(true);
        try {
            const { qStr, sStr } = formatWithParams(
                questionHtml,
                solutionHTML ?? "",
                params,
                questionTitle
            );
            setQuestionHtml(qStr);
            setSolutionHTML(sStr);
        } catch (err: any) {
            console.error("❌ Failed to process HTML:", err);
            setError(err.message || "Failed to process question HTML");
        } finally {
            setLoading(false);
        }
    }, [params, questionTitle]);

    return { questionHtml, solutionHTML, loading, error };
}
