import QuestionSettings from "./QuestionSettings";


const FilterHeader = () => {
    return (
        <>
            <div className="flex items-center justify-between gap-3">
                <h1 className="font-bold text-indigo-800 text-2xl md:text-3xl">
                    Gestalt Questions
                </h1>

                {/* Wrap to control alignment without relying on justify-self */}
                <div className="ml-auto">
                    <QuestionSettings />
                </div>
            </div>

            {/* Divider */}
            <div className="mt-3 h-2 w-full bg-indigo-300/70" />
        </>
    );
};

export default FilterHeader