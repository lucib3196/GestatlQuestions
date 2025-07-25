// React and Types
import React, { useContext, useState } from "react";
import type { QuestionInfoJson, QuestionMetadata } from "../../types/types";

// MUI Components
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

import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";


type QuestionTableProps = {
  Questions: QuestionInfoJson[] | QuestionMetadata[];
};

function hasQtypeField(question: any): question is { qtype: string } {
  return question && typeof question === "object" && "qtype" in question;
}

export function QuestionTable({ Questions }: QuestionTableProps) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const { selectedQuestion, setSelectedQuestion } = useContext(RunningQuestionSettingsContext);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleQuestionClick = (title: string) => {
    setSelectedQuestion((prev) => (prev === title ? null : title));
  };

  const shouldShowQtype = hasQtypeField(Questions[0]);

  return (
    <div className="w-3/4 mt-20">
      <TableContainer component={Paper}>
        <Table aria-label="question table">
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
              {shouldShowQtype && (
                <TableCell>
                  <div className="flex items-center gap-2 font-bold text-base text-indigo-900">
                    Question Type
                  </div>
                </TableCell>
              )}
              <TableCell>
                <div className="flex items-center gap-2 font-bold text-base text-indigo-900">
                  Is Adaptive
                </div>
              </TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {Questions.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((question, idx) => (
              <TableRow key={idx}>
                <TableCell>
                  <Checkbox />
                </TableCell>

                <TableCell>
                  <div
                    onClick={() => handleQuestionClick(question.title)}
                    className={`flex items-center gap-2 font-medium text-base cursor-pointer hover:text-red-600 hover:font-extrabold ${selectedQuestion === question.title ? "text-red-600 font-extrabold" : "text-indigo-900"
                      }`}
                  >
                    {question.title}
                  </div>
                </TableCell>

                {shouldShowQtype && (
                  <TableCell>
                    <div className="flex items-center gap-2 font-medium text-base text-indigo-900">
                      {hasQtypeField(question) ? question.qtype : "Undefined"}
                    </div>
                  </TableCell>
                )}

                <TableCell>
                  <div className="flex items-center gap-2 font-medium text-base text-indigo-900">
                    {String(question.isAdaptive).toUpperCase()}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 20]}
        count={Questions.length}
        component="div"
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </div>
  );
}
