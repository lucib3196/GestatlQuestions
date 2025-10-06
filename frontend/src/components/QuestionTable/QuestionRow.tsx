import type { QuestionMeta } from "../../types/types";
import { Checkbox, TableCell, TableRow } from "@mui/material";
import type { MinimalTestResult } from "./utils/services";

type Props = {
    question: QuestionMeta;
    isActive: boolean; // matches context.selectedQuestion
    isChecked: boolean; // from selection hook
    onToggleCheck: (idx: string, title: string, isChecked: boolean) => void;
    onClickTitle: (id: string) => void;
    testResults: MinimalTestResult[];
};

export function QuestionRow({
    question,
    isActive,
    isChecked,
    onToggleCheck,
    onClickTitle,
    testResults,
}: Props) {
    const result = testResults.find((t) => t.idx === question.id)

    return (
        <TableRow
            hover
            role="row"
            className={`transition-colors ${isActive
                    ? "bg-red-50 dark:bg-red-900/30"
                    : "hover:bg-indigo-50 dark:hover:bg-gray-800"
                }`}
        >
            {/* Checkbox */}
            <TableCell>
                <Checkbox
                    name={question.title}
                    value={question.id}
                    checked={isChecked}
                    onChange={(e) =>
                        onToggleCheck(question.id ?? "", question.title ?? "", e.target.checked)
                    }
                />
            </TableCell>

            {/* Title */}
            <TableCell>
                <div
                    onClick={() => onClickTitle(question.id ?? "")}
                    className={`flex items-center gap-2 cursor-pointer text-base font-medium transition-colors
            ${isActive
                            ? "text-red-600 dark:text-red-400 font-extrabold"
                            : "text-indigo-900 dark:text-gray-100 hover:text-red-600 hover:font-extrabold"
                        }`}
                >
                    {question.title}
                </div>
            </TableCell>

            {/* Question Type */}
            <TableCell>
                <span className="text-sm font-medium text-indigo-900 dark:text-gray-200">
                    {(question.qtypes ?? []).map((q) => q.name).join(", ")}
                </span>
            </TableCell>

            {/* Adaptive */}
            <TableCell>
                <span
                    className={`px-2 py-1 rounded-full text-xs font-semibold ${question.isAdaptive
                            ? "bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100"
                            : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                        }`}
                >
                    {question.isAdaptive ? "YES" : "NO"}
                </span>
            </TableCell>

            {/* Created By */}
            <TableCell>
                <span className="text-sm text-gray-700 dark:text-gray-300">
                    {String(question.createdBy)}
                </span>
            </TableCell>

            {/* Test Results */}
            <TableCell>
                {result ? (
                    <span
                        className={`px-2 py-1 rounded-md text-xs font-semibold ${result.pass
                                ? "bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100"
                                : "bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100"
                            }`}
                    >
                        {result.pass ? "PASS" : "FAIL"}
                    </span>
                ) : (
                    <span className="text-xs text-gray-500 dark:text-gray-400">—</span>
                )}
            </TableCell>
        </TableRow>
    )
}
