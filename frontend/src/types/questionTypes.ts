// For question types reference api/models

export type QuestionType = "Numerical" | "MultipleChoice" | "Example" | "Other";
import type { GeneralResponse } from "./responseTypes";

type questionRel = {
  name: string;
  id: number | string;
};

export type QuestionBase = {
  id?: string; // UUID
  title?: string;
  ai_generated?: boolean;
  isAdaptive?: boolean;
};

export type QuestionData = QuestionBase & {
  topics?: string[];
  languages?: string[];
  qtypes?: string[];
};

export type QuestionMeta = QuestionBase & {
  topics?: questionRel[];
  languages?: questionRel[];
  qtypes?: questionRel[];
};

export type QuestionKeys = keyof QuestionData;

export type QuestionFull = GeneralResponse & {
  question: QuestionData;
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
