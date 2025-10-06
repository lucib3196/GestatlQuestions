import { useState } from "react";
import type { Question } from "../../types/questionTypes";
import { MinimalToggle } from "../Toggles/MinimalToggle";
import { MyButton } from "../Base/Button";
import { MyModal } from "../Base/MyModal";

type ViewMode = "minimal" | "full";

// --- Mock Data for testing ---
export const MockData: Question = {
  title: "Title",
  topics: ["Topic 1", "Topic 2"],
  isAdaptive: true,
  qtypes: ["Numerical", "MultipleChoice"],
  id: "",
  ai_generated: false,
  createdBy: null,
  user_id: null,
  languages: [],
};

function UpdateQuestionMetadata() {
  return <form>
    <div>Title</div>
    <div>AI Generated</div>
    <div>Adaptive</div>
    <div>Topics</div>
    <div>Language</div>
    <div>Qtype</div>
  </form>;
}

// --- Props ---
type QuestionProps = {
  question: Question;
};

// --- Header with Toggle ---
export function QuestionHeader({ question }: QuestionProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("minimal");
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="flex flex-col  w-full max-w-5xl mx-auto space-y-6 px-4 sm:px-6 lg:px-8 mt-5">
      {/* Title + Toggle */}
      <div className="relative flex w-full items-center justify-center">
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-center">
          {question.title}
        </h1>

        {/* Toggle pinned to right */}
        <div className="bottom-0 sm:absolute sm:right-0">
          <MinimalToggle viewMode={viewMode} onChange={setViewMode} />
        </div>
      </div>

      <hr className="border-t border-gray-300 dark:border-gray-600 mx-auto w-2/3 sm:w-1/2" />

      {/* Show metadata only in full view */}
      {viewMode === "full" && (
        <div className="grid grid-cols-2">
          

          <div className="flex justify-end">
            <MyButton
              name={"Edit Question"}
              variant="primary"
              className="w-[150px] h-[50px]"
              onClick={() => setShowSettings((prev) => !prev)}
            />
            {showSettings && (
              <MyModal setShowModal={setShowSettings}>
                <UpdateQuestionMetadata />
              </MyModal>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
