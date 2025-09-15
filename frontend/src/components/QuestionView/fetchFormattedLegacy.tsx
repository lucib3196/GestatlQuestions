import type { QuestionParams } from "../../types/types";
import applyPlaceHolders from "../../utils/flattenParams";
import { processPrairielearnTags } from "../../utils/readPrairielearn";
import { getQuestionHTML, getSolutionHTML } from "../../api";
import { useState, useEffect } from "react";

export const fetchFormattedLegacyAdaptive = async (
    selectedQuestion: string | null,
    params: QuestionParams | null,
    questionTitle: string
): Promise<{ qStr: string | null; sStr: string[] | null } | undefined> => {
    type ChoiceParams = { fracQuestions: [number, number] };
    const CHOICE_PARAMS: ChoiceParams = { fracQuestions: [1.0, 1.0] };

    if (!selectedQuestion) return;

    try {
        // The Question HTML is the main one 
        // A solution file may not be present
        const [rawHtml, rawSolution] = await Promise.all([
            getQuestionHTML(selectedQuestion),
            getSolutionHTML(selectedQuestion),
        ]);
        console.log("This is the raw html", rawHtml)
        console.log("This is the data", params)
        const replacedQ = rawHtml ? applyPlaceHolders(rawHtml, params) : null
        const replacedS = rawSolution ? applyPlaceHolders(rawSolution, params) : null
        const { htmlString: qStr } = replacedQ
            ? processPrairielearnTags(replacedQ, params, "", questionTitle, CHOICE_PARAMS)
            : { htmlString: null };

        const { solutionsStrings } = replacedS
            ? processPrairielearnTags(replacedS, params, "", questionTitle, CHOICE_PARAMS)
            : { solutionsStrings: null };

        console.log(qStr)
        const sStr: string[] = solutionsStrings ? Object.values(solutionsStrings) : []
        return { qStr, sStr };
    } catch (error) {
        console.error("Failed to build question HTML/solution:", error);
    }
};

export function useFormattedLegacy(selectedQuestion: string | null, params: any, questionTitle: string) {
    const [questionHtml, setQuestionHtml] = useState<string | null>("");
    const [solutionHTML, setSolutionHTML] = useState<string[] | null>([]);

    useEffect(() => {
        let mounted = true;
        const run = async () => {
            try {
                const res = await fetchFormattedLegacyAdaptive(selectedQuestion, params, questionTitle);
                if (mounted && res) {
                    const { qStr, sStr } = res;
                    setQuestionHtml(qStr);
                    setSolutionHTML(sStr);
                }
            } catch (err) {
                console.error("Failed:", err);
            }
        };
        run();
        return () => {
            mounted = false;
        };
    }, [selectedQuestion, params]);

    return { questionHtml, solutionHTML, setQuestionHtml, setSolutionHTML };
}

