import { useEffect, useState } from "react";
import {
    Checkbox,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
} from "@mui/material";
import { useContext } from "react";
import type { SelectChangeEvent } from "@mui/material";
import { QuestionFilterContext } from "../../context/QuestionFilterContext";
import { FormControlLabel } from "@mui/material";
import QuestionSettings from "./QuestionSettings";

export function QuestionFilter() {
    const [questionType, setQuestionType] = useState("MultipleChoice");
    const { isAdaptive, setIsAdaptive, setShowAllQuestions, showAllQuestions, isAIGen, setIsAIGen } =
        useContext(QuestionFilterContext);

    const handleQuestionTypeChange = (event: SelectChangeEvent) => {
        setQuestionType(event.target.value);
    };

    const handleAdaptiveChange = (event: any) => {
        setIsAdaptive(event.target.value);
    };

    const handleQuestionChange = () => {
        setShowAllQuestions((prev) => !prev);
    };

    const handleAIGen = (event: any) => {
        setIsAIGen(event.target.value)
    }

    return (
        <div className="flex flex-col flex-wrap justify-center items-center w-full max-w-5xl space-y-8 bg-white rounded-lg shadow-md p-8 mt-10">
            {/* Header */}
            <h1 className="font-bold text-3xl text-indigo-800 mb-4 flex items-center gap-2">
                Gestalt Questions
            </h1>
            <hr className="border-3 border-indigo-300 w-full" />

            {/* Start of the filter mechanisms */}
            <div
                className="flex flex-row gap-x-8 w-full justify-evenly items-baseline flex-wrap "
                style={{ rowGap: "1.5rem", columnGap: "0.2rem" }}
            >
                <FormControl>
                    <FormControlLabel
                        onClick={handleQuestionChange}
                        control={<Checkbox />}
                        label={
                            <span className="flex items-center gap-2 font-medium text-base text-indigo-900">
                                Show All Questions
                            </span>
                        }
                    />
                </FormControl>

                <FormControl variant="outlined" sx={{ minWidth: 180 }}>
                    <InputLabel id="question-type-label">
                        <span className="flex items-center gap-2 font-medium text-base text-indigo-900">
                            Question Type
                        </span>
                    </InputLabel>
                    <Select
                        disabled={showAllQuestions}
                        labelId="question-type-label"
                        value={questionType}
                        onChange={handleQuestionTypeChange}
                        label="Question Type"
                    >
                        <MenuItem value="MultipleChoice">
                            <span className="flex items-center gap-2 font-medium text-base text-indigo-900">
                                Multiple Choice
                            </span>
                        </MenuItem>
                        <MenuItem value="numerical">
                            <span className="flex items-center gap-2 font-medium text-base text-indigo-900">
                                Numerical
                            </span>
                        </MenuItem>
                    </Select>
                </FormControl>

                <FormControl
                    variant="outlined"
                    disabled={!questionType || showAllQuestions}
                    sx={{ minWidth: 180 }}
                >
                    <InputLabel id="is-adaptive-label">isAdaptive</InputLabel>

                    <Select
                        labelId="is-adaptive-label"
                        id="is-adaptive-select"
                        value={isAdaptive}
                        onChange={handleAdaptiveChange}
                        label="isAdaptive"
                    >
                        <MenuItem value="false">False</MenuItem>
                        <MenuItem value="true">True</MenuItem>
                    </Select>
                </FormControl>

                <FormControl
                    variant="outlined"
                    disabled={!questionType || showAllQuestions}
                    sx={{ minWidth: 180 }}
                >
                    <InputLabel id="is-ai-gen-label">AIGenerated</InputLabel>

                    <Select
                        labelId="is-ai-gen-label"
                        id="is-ai-gen-select"
                        value={isAIGen}
                        onChange={handleAIGen}
                        label="AIGenerated"
                    >
                        <MenuItem value="false">False</MenuItem>
                        <MenuItem value="true">True</MenuItem>
                    </Select>
                </FormControl>

                <div className="flex self-center  items-center justify-center">
                    <QuestionSettings />
                </div>
            </div>
        </div>
    );
}
