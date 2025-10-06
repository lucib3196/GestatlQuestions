// External libraries
import { useState, useEffect } from "react";
import { useDebounce } from "@uidotdev/usehooks";

// API & Context
import { searchQuestions } from "../../api";
import { useQuestionContext } from "../../context/QuestionContext";

// Types


// Components
import AdaptiveDropDown from "./IndividualSearchForms/Adaptive";
import QuestionTypeDropDown from "./IndividualSearchForms/QuestionType";

import { ShowAllQuestionsCheckBox } from "./IndividualSearchForms/ShowAllQuestions";


type QuestionFilterProps = {
    setSearchResults: () => void
}

const QuestionFilter = ({ setSearchResults }: QuestionFilterProps) => {
    const ctx = useQuestionContext();
    const [searchTitle, _] = useState<string>("")
    const debouncedSearchTerm = useDebounce(searchTitle, 300)
    const [questionType, setQuestionType] = useState<string>("Numerical")
    const [__, setIsSearching] = useState<boolean>(false)

    const qTypes = ["Numerical", "Multiple Choice", "Other"]

    useEffect(() => {
        const fetchQuestions = async () => {
            setIsSearching(true); // optional: show loading immediately
            try {
                const retrievedQuestions = await searchQuestions({
                    filter: {
                        title: debouncedSearchTerm,
                        qtypes: [{ name: questionType.toLowerCase() }],
                        isAdaptive: ctx.isAdaptive as boolean,
                    },
                    showAllQuestions: ctx.showAllQuestions,
                });

                console.log(retrievedQuestions)

            } catch (error) {
                console.log("error")
                setSearchResults();

            } finally {
                setIsSearching(false); // optional: cleanup loading state
            }
        };
        fetchQuestions();
    }, [debouncedSearchTerm, ctx.isAdaptive, ctx.qtype, ctx.showAllQuestions]);

    return (
        <div className="flex flex-wrap flex-row gap-y-4 justify-center gap-x-2 mx-2 items-center ">
            <ShowAllQuestionsCheckBox checked={ctx.showAllQuestions} onChange={(checked) => ctx.setShowAllQuestions(checked)} />
            <QuestionTypeDropDown disabled={ctx.showAllQuestions} questionType={questionType} questionTypeOptions={qTypes} setQuestionType={setQuestionType} />
            <AdaptiveDropDown adaptiveValue={ctx.isAdaptive} setIsAdaptive={ctx.setIsAdaptive} disabled={ctx.showAllQuestions} />

        </div>
    )
}

export default QuestionFilter