import { QuestionSettings } from "../components/QuestionFilter/QuestionSettings";
import { useState } from "react";
import { QuestionFiltering } from "./../components/QuestionFilterNew/QuestionFiltering";
import { QuestionTable } from "../components/QuestionTable/QuestionTablesDB";
import QuestionPage from "./QuestionRenderPage";
function QuestionDashBoardHeader() {
  return (
    <div className="flex justify-center items-center">
      <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">
        Gestalt Questions
      </h1>
    </div>
  );
}
function QuestionSettingsToggle() {
  const [showSettings, setShowSettings] = useState<boolean>(false);
  return (
    <>
      <label className="flex flex-row items-center gap-2 cursor-pointer group py-4">
        <input
          type="checkbox"
          checked={showSettings}
          onChange={() => setShowSettings((prev) => !prev)}
          className="
              h-5 w-5 rounded-md border 
              border-surface dark:border-text-secondary 
              text-accent-teal 
              focus:ring-2 focus:ring-accent-sky 
              dark:bg-background
              transition-colors duration-300
            "
        />
        <span
          className="
              text-lg font-semibold 
              text-primary-indigo dark:text-text-secondary 
              transition-colors duration-300
            "
        >
          Show Settings
        </span>
      </label>
      <div className="mb-5">{showSettings && <QuestionSettings />}</div>
    </>
  );
}

export function QuestionViewPage() {
  const [searchResults, setSearchResults] = useState<any[]>([]);

  return (
    <section className="w-full flex flex-col items-center py-16 space-y-16">
      <div className="w-6/10 flex justify-center flex-col">
        <QuestionDashBoardHeader />
        <QuestionSettingsToggle />
        <QuestionFiltering setSearchResults={setSearchResults} />
        <section className="mt-10 flex justify-center w-full">
          <QuestionTable results={searchResults} />
        </section>
      </div>
      <div className="w-9/10">
        <QuestionPage />
      </div>
    </section>
  );
}
