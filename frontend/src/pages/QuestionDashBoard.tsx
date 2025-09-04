import QuestionFilter from "../components/QuestionFilter/QuestionFilter";
import { useState } from "react";
import type { QuestionMeta } from "../types/types";
import { QuestionTable } from "../components/QuestionTable/QuestionTablesDB";
import FilterHeader from "../components/QuestionFilter/FilterHeader";

const QuestionDashBoard = () => {
    const [retrievedQuestions, setRetrievedQuestions] = useState<QuestionMeta[]>(
        []
    );
    return (
        <main className="mx-auto w-full max-w-6xl px-4">
            <header className="flex flex-col items-center justify-center py-4">
                <FilterHeader />
            </header>

            <section
                className="mt-8 rounded-lg bg-white p-6 shadow-md"
                aria-labelledby="filters-title"
            >
                <h2 id="filters-title" className="sr-only">
                    Question Filters
                </h2>

                <QuestionFilter setSearchResults={setRetrievedQuestions} />
            </section>
            <div className="flex justify-center">
                <QuestionTable results={retrievedQuestions} />
            </div>
        </main>
    );
};

export default QuestionDashBoard;
