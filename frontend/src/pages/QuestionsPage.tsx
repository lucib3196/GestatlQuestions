import { QuestionFiltering } from "../components/QuestionFilterNew/QuestionFiltering";
import { QuestionTable } from "../components/QuestionTable/QuestionTablesDB";
import { ResizableQuestionContainer } from "../components/Question/ResizableQuestion";
import { useQuestionContext } from "../context/QuestionContext";
import SyncQuestions from "../components/QuestionSync/QuestionSync";
function QuestionDashBoardHeader() {
  return (
    <div className="flex justify-center items-center mb-6">
      <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">
        Gestalt Questions
      </h1>
    </div>
  );
}

export function QuestionViewPage() {
  const { selectedQuestionID } = useQuestionContext();

  return (
    <section className="w-full flex flex-col items-center py-12 space-y-16">
      {/* Dashboard Section */}
      <div className="w-full max-w-5xl flex flex-col items-center px-4 sm:px-6 lg:px-8">
        <QuestionDashBoardHeader />
        <SyncQuestions />

        {/* Filters & Table */}
        <div className="w-full">
          <QuestionFiltering />

          <section className="mt-10 flex justify-center w-full">
            <QuestionTable />
          </section>
        </div>
      </div>

      {/* Question Detail View */}
      {selectedQuestionID && (
        <div className="w-full px-4 sm:px-8">
          <ResizableQuestionContainer />
        </div>
      )}
    </section>
  );
}
