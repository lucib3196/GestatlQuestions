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
import { useSelectedQuestion } from "../../context/SelectedQuestionContext";
import { useSelection } from "./utils/useSelection";
import { QuestionRow } from "./QuestionRow";
import type { MinimalTestResult } from "./utils/services";
import { tableHeaderSx } from "../../styles/tableHeaderSx";
import { useTheme } from "../Generic/DarkModeToggle";
import { useQuestionContext } from './../../context/QuestionContext';


export function QuestionTable() {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { selectedQuestionID, setSelectedQuestionID } = useSelectedQuestion()
  const { isSelected, toggle } = useSelection();
  const [testResults] = useState<MinimalTestResult[]>([]);
  const [theme] = useTheme();
  const { questions } = useQuestionContext()

  const paged = useMemo(
    () => questions.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [questions, page, rowsPerPage]
  );

  const handleChangePage = (_: unknown, newPage: number) => setPage(newPage);
  const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(e.target.value, 10));
    setPage(0);
  };

  const handleQuestionClick = (id: string) => {
    console.log("This is the id of clicked", id)
    setSelectedQuestionID((prev: string | null) => (prev === id ? null : id));
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
                isActive={selectedQuestionID === q.id}
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
          count={questions.length}
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
