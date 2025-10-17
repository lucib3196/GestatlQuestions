import { QuestionSettings } from "../components/QuestionFilter/QuestionSettings";
import { useState } from "react";
import { QuestionFiltering } from "../components/QuestionFilterNew/QuestionFiltering";
import { QuestionTable } from "../components/QuestionTable/QuestionTablesDB";

import { SimpleToggle } from "../components/Base/SimpleToggle";
import { QuestionView } from "./QuestionView";
import QuestionCard from "../components/Question/QuestionCard";
import SyncQuestions from "../components/System/SyncQuestions";


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
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showSettings, setShowSettings] = useState<boolean>(false);

  return (
    <section className="w-full flex flex-col items-center py-12 space-y-16">
      {/* Dashboard Section */}
      <div className="w-full max-w-5xl flex flex-col items-center px-4 sm:px-6 lg:px-8">
        <QuestionDashBoardHeader />

        {/* Settings Toggle */}
        <div className="flex flex-col items-center w-full mb-6">
          <div className="flex flex-row items-center gap-x-10">
            <SimpleToggle
              setToggle={() => setShowSettings((prev) => !prev)}
              label="Show Settings"
              id="settings"
            />
            <SyncQuestions />
          </div>



          {showSettings && (
            <div className="mt-4 w-full">
              <QuestionSettings />
            </div>
          )}
        </div>

        {/* Filters & Table */}
        <div className="w-full">
          <QuestionFiltering setSearchResults={setSearchResults} />

          <section className="mt-10 flex justify-center w-full">
            <QuestionTable results={searchResults} />
          </section>
        </div>
      </div>

      {/* Question Detail View */}
      <div className="w-full max-w-6xl px-4 sm:px-8">
        <QuestionCard />
      </div>
    </section>
  );
}
