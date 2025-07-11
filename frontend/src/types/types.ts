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
  isCorrect: string|boolean;
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

export type QuestionMetadata = {
  question_template: string;
  image?: string;
  questionInputs: QuestionInput[];
  title: string;
  topic: string[];
  relevantCourses: string[];
  tags: string[];
  isAdaptive: string | boolean;
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
