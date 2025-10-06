import { Pill, PillContainer } from "../Base/Pill";
import type { Question, QuestionMeta } from "../../types/questionTypes";
import { FaPencil } from "react-icons/fa6";
import React, { useState } from "react";
import type { ChangeEvent } from "react";
import type { JSX } from "react";
import { MockData } from "./QuestionHeader";

//Notes: Index is the key of Question, then the value is the type of Question[key] then on change
// The argument will take in the value type and return void which is what i will implement later
type Renderers<T> = Partial<{
  [K in keyof T]: (value: T[K], onChange: (v: T[K]) => void) => JSX.Element;
}>;



function QuestionForm() {
  const [question, setQuestion] = useState<Question>(MockData)

  function updateField<K extends keyof Question>(key: K, value: Question[K]) {
    setQuestion((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <form className="space-y-4">
      {Object.keys(question).map((key) => {
        const k = key as keyof Question;
        const renderer = questionRenderer[k];
        if (!renderer) return null; // skip fields with no renderer
        return (
          <div key={k} className="flex flex-col gap-2">
            <label className="font-semibold">{k}</label>
            {renderer(question[k], (val) => updateField(k, val))}
          </div>
        );
      })}
    </form>
  );
}

const metaKeys: QuestionMeta = ["title", "qtypes", "isAdaptive", "topics"];





export default function QuestionMeta({ question: qdata }: QuestionProps) {
  const [question, setQuestion] = useState<Question>(qdata);

  metaKeys.map((key) => console.log(key));

  function handleChange<K extends keyof Question>(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const { name, value } = e.target;
    const key = name as K;

    setQuestion((prev) => ({
      ...prev,
      [key]: value,
    }));
  }

  return (
    <div className="grid grid-cols-3 sm:grid-cols-1  gap-6 mt-6">
      {QuestionForm()}
      <QuestionDataContainer
        name="Topics"
        handleChange={handleChange}
        question={question}
      >
        <QuestionTopics question={question} />
      </QuestionDataContainer>

      <QuestionDataContainer
        name="Types"
        handleChange={handleChange}
        question={question}
      >
        <QuestionTypes question={question} />
      </QuestionDataContainer>

      <QuestionDataContainer
        name="Adaptive"
        handleChange={handleChange}
        question={question}
      >
        <QuestionAdaptive question={question} />
      </QuestionDataContainer>

    </div>
  );
}

// --- Props ---
type QuestionProps = {
  question: Question;
};

// --- Data Container ---
type QuestionDataProps = {
  children: React.ReactNode;
  question: Question;
  handleChange: (e: ChangeEvent<HTMLInputElement>) => void;
  name: string;
};

export function QuestionDataContainer({
  children,
  name,
  handleChange,
  question,
}: QuestionDataProps) {
  const [editMode, setEditMode] = useState(false);


  return (
    <div className="flex flex-col sm:flex-row gap-2 sm:items-baseline">
      <FaPencil
        className="cursor-pointer text-gray-600 hover:text-blue-600"
        onClick={() => setEditMode((prev) => !prev)}
      />
      <label className="font-semibold text-base sm:text-lg">
        <input
          type="text"
          value={question[name as keyof Question] as string}
          disabled={!editMode}
          onChange={handleChange}
          className={`border rounded px-2 py-1 ${editMode
            ? "border-blue-500 bg-white dark:bg-inherit"
            : "border-transparent"
            }`}
        />
      </label>
      {children}
    </div>
  );
}

// --- Topic Pills ---
function QuestionTopics({ question }: QuestionProps) {
  return (
    <PillContainer>
      {(question.topics ?? []).map((t, i) => (
        <Pill key={i}>{t}</Pill>
      ))}
    </PillContainer>
  );
}

// --- Adaptive Pill ---
function QuestionAdaptive({ question }: QuestionProps) {
  return (
    <PillContainer>
      <Pill theme={question.isAdaptive ? "success" : "danger"}>
        {question.isAdaptive ? "True" : "False"}
      </Pill>
    </PillContainer>
  );
}

// --- Type Pills ---
function QuestionTypes({ question }: QuestionProps) {
  return (
    <PillContainer>
      {(question.qtypes ?? []).map((qt, i) => (
        <Pill key={i} theme="secondary">
          {qt}
        </Pill>
      ))}
    </PillContainer>
  );
}
