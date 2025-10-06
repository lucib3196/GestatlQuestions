import { RunningQuestionSettingsContext } from "../context/RunningQuestionContext";
import { useContext,  } from "react";

function QuestionPage() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
   

    if (!selectedQuestion) return null;

    return (
        <>Div</>
        // <div className="relative w-full max-w-6xl mx-auto flex flex-col items-center border border-gray-200 dark:border-gray-700 shadow-md rounded-xl mt-10 p-6 transition-colors">
        //     {/* Action bar */}
        //     <div className="flex flex-row gap-4 mb-6 self-end">
        //         <button
        //             className="px-5 py-2 rounded-md bg-indigo-600 text-white font-semibold shadow hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-400 focus:outline-none transition"
        //             onClick={() => setEditCode((prev) => !prev)}
        //         >
        //             {editCode ? "Close Editor" : "Edit Code"}
        //         </button>

        //         <button
        //             className="px-5 py-2 rounded-md bg-green-500 text-white font-semibold shadow opacity-70 cursor-not-allowed"
        //             disabled
        //         >
        //             Submit Review
        //         </button>
        //     </div>

        //     {/* Panels */}
        //     <div className="w-full h-[70vh] min-h-[500px]">
                
        //             {editCode && (
                        
        //                     <div className="w-full h-full border-r border-gray-200 dark:border-gray-700 overflow-auto">
        //                         <QuestionCodeEditor />
        //                     </div>
        //                 </Panel>
        //             )}

        //             <Panel id="question" order={2} defaultSize={editCode ? 60 : 100}>
        //                 <div className="w-full h-full px-4 bg-white dark:bg-background overflow-auto">
                            // <RenderAdaptiveQuestion />
        //                 </div>
        //             </Panel>
        //         </PanelGroup>
        //     </div>
        // </div>
    );
}

export default QuestionPage;
