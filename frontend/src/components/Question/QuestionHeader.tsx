import type { Question } from "../../types/questionTypes";
import { Pill, type PillTheme } from "../Base/Pill";
import { SimpleToggle } from "../Base/SimpleToggle";
import { useState } from "react";


interface FormatMetaDataProps {
  val: string[] | string;
  label: string;
  theme?: PillTheme;
}

export const FormatMetaData = ({
  val,
  label,
  theme = "primary",
}: FormatMetaDataProps) => {
  const values = Array.isArray(val) ? val : [val];

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="font-semibold text-sm text-gray-700 dark:text-gray-300">
        {label}:
      </span>
      {values.map((v, i) => (
        <Pill key={i} theme={theme}>
          {v}
        </Pill>
      ))}
    </div>
  );
};

interface GenericInfoProps {
  title: string;
  data?: string[];
  theme?: PillTheme;
}

const GenericInfo = ({
  title,
  data = [],
  theme = "secondary",
}: GenericInfoProps) => (
  <div className="flex flex-col sm:flex-row sm:items-start sm:gap-x-4 gap-y-2">
    <p className="sm:min-w-[140px] text-base font-semibold text-gray-800 dark:text-gray-200">
      {title}:
    </p>
    <div className="flex flex-wrap gap-2">
      {data.length > 0 ? (
        data.map((val, id) => (
          <Pill key={id} theme={theme}>
            {val}
          </Pill>
        ))
      ) : (
        <span className="text-sm italic text-gray-500 dark:text-gray-400">
          No data
        </span>
      )}
    </div>
  </div>
);

export default function QuestionInfo({
  qmetadata,
}: {
  qmetadata:  Question;
}) {
  const { topics = [], isAdaptive } = qmetadata;

  return (
    <div className="flex flex-col gap-5 p-2 sm:p-4">
      <GenericInfo
        title="Topics"
        data={topics.map((t) => t)}
        theme="info"
      />

      <div className="flex items-center gap-4">
        <p className="text-base font-semibold text-gray-800 dark:text-gray-200">
          Adaptive:
        </p>
        <Pill theme={isAdaptive ? "success" : "danger"}>
          {isAdaptive ? "Adaptive" : "Static"}
        </Pill>
      </div>
    </div>
  );
}

// --- Header with Toggle ---
export function QuestionHeader({ question }: { question: Question }) {
  const [showMeta, setShowMeta] = useState(true);
  return (
    <div className="flex flex-col items-center w-full max-w-5xl mx-auto space-y-6 px-4 sm:px-6 lg:px-8 mt-8">
      {/* Title Section */}
      <div className="relative flex flex-col sm:flex-row items-center justify-between gap-4 ">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-center sm:text-left text-gray-800 dark:text-gray-100 tracking-tight">
          {question.title}
        </h1>
      </div>
      <SimpleToggle
        setToggle={() => setShowMeta((prev) => !prev)}
        label="Show Question Metadata"
        id="meta-toggle"
        checked={showMeta}
      />
      {/* Divider */}
      <hr className="border-t border-gray-300 dark:border-gray-700 mx-auto w-2/3 sm:w-1/2" />
      {showMeta && <QuestionInfo qmetadata={question} />}
    </div>
  );
}
