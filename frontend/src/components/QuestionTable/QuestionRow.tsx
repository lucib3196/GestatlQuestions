import type { QuestionDB } from "../../types/types";
import { Checkbox, TableCell, TableRow } from "@mui/material";
import type { MinimalTestResult } from "./utils/services";
type Props = {
    question: QuestionDB;
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
    return (
        <TableRow hover role="row">
            <TableCell>
                <Checkbox
                    name={question.title}
                    value={question.id}
                    checked={isChecked}
                    onChange={(e) =>
                        onToggleCheck(question.id, question.title, e.target.checked)
                    }
                />
            </TableCell>

            <TableCell>
                <div
                    onClick={() => onClickTitle(question.id)}
                    className={[
                        "flex items-center gap-2 font-medium text-base cursor-pointer",
                        isActive
                            ? "text-red-600 font-extrabold"
                            : "text-indigo-900 hover:text-red-600 hover:font-extrabold",
                    ].join(" ")}
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

            <TableCell>
                <div className="flex items-center gap-2 font-medium text-base text-indigo-900">
                    {testResults.find((t) => t.idx === question.id)?.pass ?? 0}
                </div>
            </TableCell>
        </TableRow>
    );
}
