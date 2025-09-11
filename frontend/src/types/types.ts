export type QuestionParams = {
  params: Record<string, string | number | any>;
  correct_answers: Record<string, string | number>;
  nDigits: number;
  sigfigs: number;
};

export type QuestionData = {
  question_template: string;
  params: QuestionParams;
};

export type MultipleChoiceOption = {
  name: string;
  isCorrect: string | boolean;
};

type BaseQuestionInput = {
  name: string;
  label: string;
  required?: boolean;
};

export type NumberInput = BaseQuestionInput & {
  qtype: "number";
  comparison: "sigfig";
  digits?: number;
  units?: string;
};

type MultipleChoiceInput = BaseQuestionInput & {
  qtype: "multiple_choice";
  options: MultipleChoiceOption[];
  shuffle?: boolean;
};

type CheckboxInput = BaseQuestionInput & {
  qtype: "checkbox";
  options: string[];
  correctOptions: string[];
  shuffle?: boolean;
};

export type QuestionInput = NumberInput | MultipleChoiceInput | CheckboxInput;

export type Solution = {
  solution_hint: string[];
};

export type QuestionRender = {
  question_template: string;
  questionInputs: QuestionInput[];
  image?: string;
  solution_render?: Solution;
};

export type QuestionMetadata = {
  rendering_data: QuestionRender[];
  title: string;
  topic: string[];
  relevantCourses: string[];
  tags: string[];
  isAdaptive: string | boolean;
  createdBy?: string;
};

// Old structure to be changed later
export type QuestionInfoJson = {
  question: string;
  title: string;
  topic: string[];
  relevant_clourses: string[];
  tags: string[];
  prereqs: string[];
  isAdaptive: string | boolean;
};

export type QuestionDB = {
  id: string;
  user_id: number;
  qtype: string[];
  title: string;
  topic: string[];
  isAdaptive: string | boolean;
  createdBy: string;
  language: string[];
  ai_generated: string[];
};

// New Interfaces

type GenericRelationship = {
  name: string;
  id?: string;
};
export type QuestionMeta = {
  title?: string;
  ai_generated?: boolean;
  createdBy?: string;
  id?: string;
  isAdaptive?: boolean;
  user_id?: number;
  topics?: GenericRelationship[];
  qtypes?: GenericRelationship[];
  languages?: GenericRelationship[];
};

export type FileData = {
  filename: string;
  content: string;
};
