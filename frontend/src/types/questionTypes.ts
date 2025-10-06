export type QuestionType = "Numerical" | "MultipleChoice" | "Example" | "Other";
import type { GeneralResponse } from "./responseTypes";

export type Question = {
  id: string; // UUID
  title: string;
  ai_generated: boolean;
  isAdaptive: boolean;
  createdBy: string | null;
  user_id: number | null;
  topics: string[];
  languages: string[];
  qtypes: string[];
};
export type QuestionKeys = keyof Question;
export type QuestionMeta = QuestionKeys[];

export type QuestionFull = GeneralResponse & {
  question: Question;
  files: FileData[];
};

export type FileData = {
  filename: string;
  content: string;
};

export type FileName = GeneralResponse & {
  files: FileData[];
  file_paths: string[];
};
