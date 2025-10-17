import React, { useMemo, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Paper,
} from "@mui/material";
import { useQuestion } from "../../context/QuestionSelectionContext";
import { useSelection } from "./utils/useSelection";
import { QuestionRow } from "./QuestionRow";
import type { QuestionMeta } from "../../types/types";
import type { MinimalTestResult } from "./utils/services";
import { tableHeaderSx } from "../../styles/tableHeaderSx";
import { useTheme } from "../Generic/DarkModeToggle";

type Props = { results: QuestionMeta[] };

export function QuestionTable({ results }: Props) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { questionID, setQuestionID } = useQuestion()
  const { isSelected, toggle } = useSelection();
  const [testResults] = useState<MinimalTestResult[]>([]);
  const [theme] = useTheme();

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
    console.log("This is the id of clicked", id)
    setQuestionID((prev: string | null) => (prev === id ? null : id));
  };

  return (
    <div className="w-full lg:w-3/4 mt-10">
      <TableContainer
        component={Paper}
        className="rounded-lg shadow-md dark:bg-gray-900"
      >
        <Table aria-label="question table" stickyHeader>
          <TableHead>
            <TableRow>
              {[
                "Select",
                "Question Title",
                "Question Type",
                "Is Adaptive",
                // "Created By",
                // "Test Results",
              ].map((h) => (
                <TableCell key={h} sx={tableHeaderSx(theme)}>
                  {h}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {paged.map((q) => (
              <QuestionRow
                key={q.id}
                question={q}
                isActive={questionID === q.id}
                isChecked={isSelected(q.id ?? "")}
                onToggleCheck={toggle}
                onClickTitle={handleQuestionClick}
                testResults={testResults}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <div className="flex justify-end mt-4">
        <TablePagination
          rowsPerPageOptions={[5, 10, 20]}
          count={results.length}
          component="div"
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          sx={{
            color:
              theme === "dark" ? "var(--text-primary)" : "var(--primary-blue)",
          }}
        />
      </div>
    </div>
  );
}
