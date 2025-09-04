import type { QuestionParams } from "../../types/types";
import applyPlaceHolders from "../../utils/flattenParams";
import { processPrairielearnTags } from "../../utils/readPrairielearn";
import { getQuestionHTML, getSolutionHTML } from "../../api";
import { useState, useEffect } from "react";

export const fetchFormattedLegacyAdaptive = async (
    selectedQuestion: string | null,
    params: QuestionParams | null
): Promise<{ qStr: string; sStr: string[] } | undefined> => {
    type ChoiceParams = { fracQuestions: [number, number] };
    const CHOICE_PARAMS: ChoiceParams = { fracQuestions: [1.0, 1.0] };

    if (!selectedQuestion || !params) return;

    try {
        const [rawHtml, rawSolution] = await Promise.all([
            getQuestionHTML(selectedQuestion),
            getSolutionHTML(selectedQuestion),
        ]);

        const replacedQ = applyPlaceHolders(rawHtml, params);
        const replacedS = applyPlaceHolders(rawSolution, params);

        const { htmlString: qStr } = processPrairielearnTags(
            replacedQ,
            params,
            "",
            "",
            CHOICE_PARAMS
        );
        const { solutionsStrings } = processPrairielearnTags(
            replacedS,
            params,
            "",
            "",
            CHOICE_PARAMS
        );

        const sStr: string[] = Object.values(solutionsStrings);
        return { qStr, sStr };
    } catch (error) {
        console.error("Failed to build question HTML/solution:", error);
    }
};

export function useFormattedLegacy(selectedQuestion: string | null, params: any) {
    const [questionHtml, setQuestionHtml] = useState<string>("");
    const [solutionHTML, setSolutionHTML] = useState<string[]>([]);

    useEffect(() => {
        let mounted = true;
        const run = async () => {
            try {
                const res = await fetchFormattedLegacyAdaptive(selectedQuestion, params);
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

