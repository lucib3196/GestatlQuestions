import {
    Checkbox,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    type SelectChangeEvent,
} from "@mui/material";
import { FormControlLabel } from "@mui/material";
import { useQuestionContext } from "../../context/QuestionContext";
import { useDebounce } from "@uidotdev/usehooks";
import React, { useContext, useState } from "react";
import api from "../../api";
import type { QuestionDB } from "../../types/types";
import { QuestionTable } from "../QuestionTable/QuestionTablesDB";
import QuestionSettings from "./QuestionSettings";
import { RunningQuestionSettingsContext } from './../../context/RunningQuestionContext';

const FilterHeader = () => {
    return (
        <header className="w-full">
            <div className="flex items-center justify-between gap-3">
                <h1 className="font-bold text-indigo-800 text-2xl md:text-3xl">
                    Gestalt Questions
                </h1>

                {/* Wrap to control alignment without relying on justify-self */}
                <div className="ml-auto">
                    <QuestionSettings />
                </div>
            </div>

            {/* Divider */}
            <div className="mt-3 h-2 w-full bg-indigo-300/70" />
        </header>
    );
};

const QuestionFilterDB = () => {
    const ctx = useQuestionContext();
    const [searchTerm, setSearchTerm] = useState<string>("");
    const [results, setResults] = useState<QuestionDB[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const debouncedSearchTerm = useDebounce(searchTerm, 300);
    const [questionType, setQuestionType] = useState("MultipleChoice");
    const { codeRunningSettings } = useContext(RunningQuestionSettingsContext)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchTerm(e.target.value);
    };

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const qTitle = formData.get("question_title");
        setSearchTerm(typeof qTitle === "string" ? qTitle : "");
        e.currentTarget.reset();
        e.currentTarget.focus();
    };

    React.useEffect(() => {
        const searchQuestions = async () => {
            let retrievedQuestions = [];

            setIsSearching(true);
            try {
                const data = await api.post(
                    "/db_questions/filter_question",
                    !ctx.showAllQuestions
                        ? {
                            title: debouncedSearchTerm,
                            qtype: ctx.qtype[0],
                            isAdaptive: ctx.isAdaptive as boolean,
                        }
                        : {}
                );
                retrievedQuestions = data.data || [];
                setIsSearching(false);
                setResults(retrievedQuestions);
            } catch (error) {
                console.log(error);
            }
        };

        searchQuestions();
    }, [debouncedSearchTerm, ctx.isAdaptive, ctx.qtype, ctx.showAllQuestions]);

    return (
        <>
            <div className=" flex flex-wrap  flex-col  mt-10 w-full max-w-8/10 rounded-lg bg-white p-8 shadow-md">
                <FilterHeader />

                <form
                    onSubmit={handleSubmit}
                    className="mt-6 flex flex-wrap flex-col items-center gap-6"
                >
                    {/* Show All */}
                    {/*  */}
                    <div className="flex flex-wrap flex-row gap-y-4 w-full justify-center gap-x-2 mx-2 items-center ">
                        <FormControl className="flex-[1_1_10rem] min-w-48 max-w-xl">
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={ctx.showAllQuestions}
                                        onChange={(_, checked) => ctx.setShowAllQuestions(checked)}
                                    />
                                }
                                label={
                                    <span className="text-base font-medium text-indigo-900">
                                        Show All Questions
                                    </span>
                                }
                            />
                        </FormControl>

                        {/* Question Type */}
                        <FormControl className=" flex-[1_1_10rem] min-w-48 max-w-xl">
                            <InputLabel id="question-type-label">
                                <span className="text-base font-medium text-indigo-900">
                                    Question Type
                                </span>
                            </InputLabel>
                            <Select
                                labelId="question-type-label"
                                value={questionType}
                                onChange={(e: SelectChangeEvent) =>
                                    setQuestionType(e.target.value)
                                }
                                label="Question Type"
                                disabled={ctx.showAllQuestions}
                            >
                                <MenuItem value="MultipleChoice">
                                    <span className="text-base font-medium text-indigo-900">
                                        Multiple Choice
                                    </span>
                                </MenuItem>
                                <MenuItem value="numerical">
                                    <span className="text-base font-medium text-indigo-900">
                                        Numerical
                                    </span>
                                </MenuItem>
                            </Select>
                        </FormControl>

                        {/* isAdaptive */}
                        <FormControl
                            className="flex-[1_1_10rem] min-w-48 max-w-xl"
                            disabled={!questionType || ctx.showAllQuestions}
                        >
                            <InputLabel id="is-adaptive-label">isAdaptive</InputLabel>
                            <Select
                                labelId="is-adaptive-label"
                                id="is-adaptive-select"
                                value={String(ctx.isAdaptive)}
                                onChange={(e) => ctx.setIsAdaptive(e.target.value === "true")}
                                label="isAdaptive"
                            >
                                <MenuItem value="false">False</MenuItem>
                                <MenuItem value="true">True</MenuItem>
                            </Select>
                        </FormControl>
                    </div>

                    {/* Search row (takes remaining width, wraps to new line on small screens) */}
                    <div className="flex grow basis-full w-6/10 items-center gap-3">
                        <input
                            name="question_title"
                            type="text"
                            value={searchTerm}
                            onChange={handleChange}
                            disabled={ctx.showAllQuestions}
                            placeholder="Question Title"
                            className={`w-full flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500 ${ctx.showAllQuestions
                                ? "bg-gray-300 hover:cursor-not-allowed"
                                : ""
                                }`}
                        />
                        <button
                            type="submit"
                            disabled={isSearching || ctx.showAllQuestions}
                            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                        >
                            {isSearching ? "..." : "Search"}
                        </button>
                    </div>
                </form>
            </div>
            <QuestionTable results={results} />
        </>
    );
};
export default QuestionFilterDB;
