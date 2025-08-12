import React, { useState } from "react";
import type { QuestionDB } from "../../types/types";

import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TablePagination,
    TableRow,
    Paper,
    Checkbox,
} from "@mui/material";
import { MdDelete } from "react-icons/md";
import api from "../../api";

type QuestionTableProsp = {
    results: QuestionDB[];
};

type CheckedQuestion = {
    idx: string; // The idx of the question
    title: string;
    isChecked: boolean;
};

export function QuestionTable({ results }: QuestionTableProsp) {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);

    const [selectedQuestion, setSelectedQuestion] = useState("");

    const [checkedQuestion, setCheckedQuestion] = useState<CheckedQuestion[]>([]);

    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    };
    const handleChangeRowsPerPage = (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleQuestionClick = (title: string) => {
        console.log("Question Clicked", title);
        setSelectedQuestion(title);
    };

    const handleCheckBoxClick = (event: React.ChangeEvent<HTMLInputElement>) => {
        const { name, checked, value, } = event.target;

        setCheckedQuestion((prev) => {
            const next = [...(prev ?? [])];
            const i = next.findIndex((q) => q.idx === String(value));

            if (i === -1) {
                // Not in list yet
                if (checked)
                    next.push({ idx: String(value), title: name, isChecked: true });
                return next;
            }

            // Already in list
            if (!checked) {
                // remove when unchecked
                next.splice(i, 1);
                return next;
            }

            // update when checked
            next[i] = { ...next[i], title: name, isChecked: true };
            return next;
        });
    };

    const handleDelete = async () => {
        const toDelete = checkedQuestion.filter((q) => q.isChecked);
        if (toDelete.length === 0) {
            console.log("No questions selected for deletion.");
            return;
        }

        try {
            const request = toDelete.map((q) =>
                api.post("/db_questions/delete_question", null, {
                    params: { question_id: q.idx },
                })
            );

            const response = await Promise.all(request);
            console.log(response.map((r) => r.data));

            setCheckedQuestion((prev) => prev.filter((q) => !q.isChecked));
        } catch (err) {
            console.log("Delete failed");
        }
    };

    const hasSelection = checkedQuestion.length > 0;

    return (
        <div className="w-3/4 mt-20">
            <div className="w-full border flex items-center justify-center mb-10 py-3">
                <button
                    type="button"
                    onClick={hasSelection ? handleDelete : undefined}
                    disabled={!hasSelection}
                    title={hasSelection ? `Delete ${checkedQuestion.length} selected` : "Select questions to enable delete"}
                    aria-label="Delete selected questions"
                    className={[
                        "inline-flex items-center rounded-md p-2 transition",
                        hasSelection
                            ? "text-red-600 hover:text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                            : "text-gray-400 cursor-not-allowed"
                    ].join(" ")}
                >
                    <MdDelete size={20} />
                    <span className="sr-only">Delete</span>
                </button>
            </div>
            <TableContainer component={Paper}>
                <Table aria-label="question table">
                    {/* Header  */}
                    <TableHead>
                        <TableRow>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">
                                    Select
                                </div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center font-bold gap-2 text-base text-indigo-900">
                                    Question Title
                                </div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">
                                    Question Type
                                </div>
                            </TableCell>

                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">
                                    Is Adaptive
                                </div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">
                                    CreatedBy
                                </div>
                            </TableCell>
                        </TableRow>
                    </TableHead>

                    {/* Actual content */}
                    <TableBody>
                        {results
                            .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                            .map((question, idx) => (
                                <TableRow key={idx}>
                                    <TableCell>
                                        <Checkbox
                                            name={question.title}
                                            id={String(idx)}
                                            value={question.id}
                                            onChange={handleCheckBoxClick}
                                        />
                                    </TableCell>

                                    {/* Title of the Question */}
                                    <TableCell>
                                        <div
                                            onClick={() => handleQuestionClick(question.title)}
                                            className={`flex items-center gap-2 font-medium text-base cursor-pointer hover:text-red-600 hover:font-extrabold ${selectedQuestion === question.title
                                                ? "text-red-600 font-extrabold"
                                                : "text-indigo-900"
                                                }`}
                                        >
                                            {question.title}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex items-center gap-2 font-medium text-base text-indigo-900">
                                            {question.qtype}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex items-center gap-2 font-medium text-base text-indigo-900">
                                            {String(question.isAdaptive).toUpperCase()}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex items-center gap-2 font-medium text-base text-indigo-900">
                                            {String(question.createdBy)}
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                rowsPerPageOptions={[5, 10, 20]}
                count={results.length}
                component="div"
                page={page}
                rowsPerPage={rowsPerPage}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
            />
        </div>
    );
}
