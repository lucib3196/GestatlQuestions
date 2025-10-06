import { useState, useEffect } from "react";

import { useDebounce } from "@uidotdev/usehooks";

import ModularFilter from "./ModularFilter";
import type { Flag } from "./ModularFilter";
import { searchQuestions } from "../../api";




type QuestionFilterProps = {
    setSearchResults: (val: any[]) => void // ideally use: setSearchResults: (val: Question[]) => void
}

const flags: Flag[] = [
    { key: "adaptive", label: "Adaptive", type: "checkbox" },
    { key: "reviewed", label: "Reviewed", type: "checkbox" },
    { key: "language", label: "Language", type: "select", options: ["Python", "JavaScript", "Both"] }
]


export function QuestionFiltering({ setSearchResults }: QuestionFilterProps) {
    const [toggle, setToggle] = useState(false)
    const [searchTitle, setSearchTitle] = useState<string>("")
    const debouncedSearchTerm = useDebounce(searchTitle, 300)
    const [isSearching, setIsSearching] = useState<boolean>(false)

    // TODO: Handle logic
    const handleFilters = (activeFilters: Record<string, any>) => {
        console.log(activeFilters)
    }

    useEffect(() => {
        const fetchQuestions = async () => {
            if (!debouncedSearchTerm.trim()) {
                setSearchResults([])
                return
            }

            setIsSearching(true)
            try {
                const retrievedQuestions = await searchQuestions({
                    filter: { title: debouncedSearchTerm },
                    showAllQuestions: true,
                })
                setSearchResults(retrievedQuestions)
            } catch (error) {
                console.error("Error fetching questions:", error)
                setSearchResults([])
            } finally {
                setIsSearching(false)
            }
        }

        fetchQuestions()
    }, [debouncedSearchTerm, setSearchResults])

    return (
        <div className="flex flex-col grow basis-full w-full items-center gap-3">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 w-full">
                {/* Search Bar */}
                <input
                    type="text"
                    value={searchTitle}
                    onChange={(e) => setSearchTitle(e.target.value)}
                    placeholder="Search questions by title..."
                    className="flex-1 rounded-md border border-gray-300 dark:border-gray-700 
               bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200 
               px-4 py-2 focus:outline-none focus:ring-2 
               focus:ring-blue-500 transition"
                />

                {/* Show All Toggle */}
                <label
                    htmlFor="showAll"
                    className="flex items-center space-x-2 cursor-pointer text-gray-700 dark:text-gray-300 text-sm font-medium"
                    onClick={() => setToggle((prev) => !prev)}
                >
                    <input
                        type="checkbox"
                        name="showAll"
                        id="showAll"
                        className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                    />
                    <span>Toggle Additional Filters</span>
                </label>
            </div>

            {toggle && <ModularFilter flags={flags} onChange={handleFilters} disabled={!toggle} />}

            {isSearching && (
                <span className="text-sm text-gray-500 dark:text-gray-400">
                    Searching...
                </span>
            )}
        </div>
    )
}