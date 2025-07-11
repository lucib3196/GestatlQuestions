import { useEffect, useState, useContext } from "react";
import api from "../../api";
import type { QuestionInfoJson } from "../../types/types";
import { QuestionTable } from "./QuestionTables";
import { QuestionFilterContext } from "./../../context/QuestionFilterContext";
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";
import type { QuestionMetadata } from "../../types/types";




function LocalQuestionsView() {
    const [questionData, setQuestionData] = useState<QuestionInfoJson[] | QuestionMetadata[]>([]);
    const { isAdaptive, showAllQuestions } = useContext(QuestionFilterContext);
    const { renderingSettings } = useContext(QuestionSettingsContext);

    // Filter more to be added
    async function fetchFilteredQuestions(filters: object) {
        try {
            let url;
            if (renderingSettings === "new") {
                url = "/local_questions/filter_questions/new_format";
            } else {
                url = "/local_questions/filter_questions";
            }
            const response = await api.get(url, {
                params: filters,
            });
            console.log(response.data)
            setQuestionData(response.data);
        } catch (error) {
            console.error("Failed to fetch filtered questions:", error);
            return [];
        }
    }

    let filter;
    if (showAllQuestions) {
        filter = {};
    } else {
        filter = {
            isAdaptive: isAdaptive,
        };
    }
    useEffect(() => {
        fetchFilteredQuestions(filter);
    }, [isAdaptive, showAllQuestions, renderingSettings]);

    return <QuestionTable Questions={questionData}></QuestionTable>;
}

export default LocalQuestionsView;
