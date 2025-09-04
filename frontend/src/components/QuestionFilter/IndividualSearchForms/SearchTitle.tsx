

type SearchTitleProps = {
    searchTerm: string;
    setSearchTerm: (val: string) => void;
    isSearching: boolean;
    disabled?: boolean

}

const SearchTitle = ({ searchTerm, setSearchTerm, isSearching, disabled }: SearchTitleProps) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchTerm(e.target.value);
    };
    return (
        <div className="flex grow basis-full w-6/10 items-center gap-3">
            <input
                name="question_title"
                type="text"
                value={searchTerm}
                onChange={handleChange}
                disabled={disabled}
                placeholder="Question Title"
                className={`w-full flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500 ${disabled
                    ? "bg-gray-300 hover:cursor-not-allowed"
                    : ""
                    }`}
            />
            <button
                type="submit"
                disabled={isSearching || disabled}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            >
                {isSearching ? "..." : "Search"}
            </button>
        </div>
    )
}

export default SearchTitle