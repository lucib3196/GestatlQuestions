import { useState } from "react";
import ModularFilter from "./ModularFilter";
import type { Flag } from "./ModularFilter";
import { useRetrievedFilteredQuestions } from "../../api";
import { useDebounce } from "@uidotdev/usehooks";
import SearchBar from "../Base/SearchBar";
import { SimpleToggle } from "../Base/SimpleToggle";

type QuestionFilterProps = {
  setSearchResults: (val: any[]) => void; // ideally use: setSearchResults: (val: Question[]) => void
};

const flags: Flag[] = [
  { key: "adaptive", label: "Adaptive", type: "checkbox" },
  { key: "reviewed", label: "Reviewed", type: "checkbox" },
  {
    key: "language",
    label: "Language",
    type: "select",
    options: ["Python", "JavaScript", "Both"],
  },
];

export function QuestionFiltering({ setSearchResults }: QuestionFilterProps) {
  const [toggle, setToggle] = useState(false);
  const [searchTitle, setSearchTitle] = useState<string>("");
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showAllQuestions, setShowAllQuestions] = useState<boolean>(false);

  const debouncedSearchTerm = useDebounce(searchTitle, 300);

  // TODO: Handle logic
  const handleFilters = (activeFilters: Record<string, any>) => {
    console.log(activeFilters);
  };

  useRetrievedFilteredQuestions({
    searchTitle: debouncedSearchTerm,
    showAllQuestions,
    setSearchResults,
    setIsSearching,
  });

  return (
    <div className="flex flex-col w-full grow basis-full items-center gap-5 p-4 rounded-lg bg-white dark:bg-gray-900 shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 w-full">
        {/* Search Bar */}
        <div className="flex-1 w-full">
          <SearchBar
            value={searchTitle}
            setValue={(v) => setSearchTitle(v)}
            disabled={showAllQuestions}
          />
        </div>

        {/* Toggles */}
        <div className="flex flex-col md:flex-row items-center gap-3">
          <SimpleToggle
            setToggle={() => setToggle((prev) => !prev)}
            label="Show Additional Filters"
            id="showAllFilters"
          />
          <SimpleToggle
            setToggle={() => setShowAllQuestions((prev) => !prev)}
            label="Show All Questions"
            id="showAllQuestions"
          />
        </div>
      </div>

      {/* Filters */}
      {toggle && (
        <div className="w-full mt-2">
          <ModularFilter
            flags={flags}
            onChange={handleFilters}
            disabled={!toggle}
          />
        </div>
      )}

      {/* Searching Indicator */}
      {isSearching && (
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400 animate-pulse">
          Searching...
        </span>
      )}
    </div>
  );
}
