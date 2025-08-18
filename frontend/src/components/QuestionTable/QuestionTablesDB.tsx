


import React, { useContext, useMemo, useState } from "react";
import {
    Table, TableBody, TableCell, TableContainer, TableHead,
    TablePagination, TableRow, Paper,
} from "@mui/material";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import { useSelection } from "./utils/useSelection";
import { deleteQuestions, runQuestionTest, downloadQuestions } from "./utils/services";
import { QuestionRow } from './QuestionRow';
import { TableToolbar } from "./TableToolBar";
import type { QuestionDB } from "../../types/types";
import type { MinimalTestResult } from "./utils/services";
import { toast } from "react-toastify";
type Props = { results: QuestionDB[] };


export function QuestionTable({ results }: Props) {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const { selectedQuestion, setSelectedQuestion } = useContext(RunningQuestionSettingsContext);
    const { isSelected, selected, toggle, clear, count } = useSelection();
    const [testResults, setTestResults] = useState<MinimalTestResult[]>([])

    const paged = useMemo(
        () => results.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
        [results, page, rowsPerPage]
    );
    const handleChangePage = (_: unknown, newPage: number) => setPage(newPage);
    const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(e.target.value, 10));
        setPage(0);
    };
    const handleQuestionClick = (id: string) => {
        setSelectedQuestion((prev: string | null) => (prev === id ? null : id));
    };

    const handleDelete = async () => {
        if (!count) return;
        try {
            await deleteQuestions(selected.map((s) => s.id))
        } catch {
            console.error("Delete failed")
        }
    }

    const handleRunTests = async () => {
        try {
            const ids = selected.map((s) => s.id)
            const res = await runQuestionTest(ids);
            setTestResults(res)
            toast.success("Ran Test Succesfully")
        }
        catch (e) {
            console.error("Run tests failed", e);
        }
    }

    const handleDownload = async () => {
        try {
            const ids = selected.map((s) => s.id)
            const res = await downloadQuestions(ids)
        } catch (error) {
            console.log(error)

        }

    }
    return (
        <div className="w-3/4 mt-20">
            <TableToolbar canAct={count > 0} count={count} onDelete={handleDelete} onRunTests={handleRunTests} onHandleDownload={handleDownload} />

            <TableContainer component={Paper}>
                <Table aria-label="question table">
                    <TableHead>
                        <TableRow>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">Select</div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">Question Title</div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">Question Type</div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">Is Adaptive</div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">CreatedBy</div>
                            </TableCell>
                            <TableCell>
                                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">Test Results</div>
                            </TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {paged.map((q) => (
                            <QuestionRow
                                key={q.id}
                                question={q}
                                isActive={selectedQuestion === q.id}
                                isChecked={isSelected(q.id)}
                                onToggleCheck={toggle}
                                onClickTitle={handleQuestionClick}
                                testResults={testResults}

                            />
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