import {
    useState,
} from "react";
import SectionContainer from "../Base/SectionContainer";

import {
    Panel as RPanel,
    PanelGroup,
    PanelResizeHandle,
} from "react-resizable-panels";
import { SolutionPanel } from "./SolutionPanel";
import QuestionCard from "./QuestionCard";


export function ResizableQuestionContainer() {
    const [showSolution, setShowSolution] = useState(false);
    const [solution, setSolution] = useState<string[] | null>(null);


    return (
        <SectionContainer
            id="questionView"
            style="primary"
            className="relative flex flex-col w-full h-full p-4 sm:p-6 bg-gray-50 dark:bg-gray-900 rounded-2xl shadow-md border border-gray-200 dark:border-gray-700"
        >
            <div className="w-full border-black">
                Content

            </div>

            <PanelGroup
                className="flex w-full max-h-4/10 rounded-lg overflow-hidden border border-gray-300 dark:border-gray-700"
                autoSaveId="conditional"
                direction="horizontal"
            >
                {/* Left Solution Panel */}
                {showSolution && (
                    <RPanel
                        id="solution-panel"
                        order={1}
                        defaultSize={50}
                        minSize={25}
                        className="bg-white dark:bg-gray-800 border-r border-gray-300 dark:border-gray-700 p-4 overflow-auto"
                    >
                        <SolutionPanel solution={solution ?? []} />
                    </RPanel>
                )}

                {/* Resize Handle */}
                <PanelResizeHandle className="w-3 cursor-col-resize bg-blue-100 hover:bg-blue-400 dark:bg-blue-700 dark:hover:bg-blue-600 transition-all rounded-sm" />

                {/* Right Question Panel */}
                <RPanel
                    id="question-view"
                    order={2}
                    defaultSize={50}
                    minSize={30}
                    className="flex flex-col items-center justify-center bg-white dark:bg-gray-800 p-6"
                >
                    <QuestionCard setShowSolution={setShowSolution} setSolution={setSolution} />
                </RPanel>
            </PanelGroup>
        </SectionContainer>
    );
}