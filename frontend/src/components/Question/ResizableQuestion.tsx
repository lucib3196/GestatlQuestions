import { useState } from "react";
import SectionContainer from "../Base/SectionContainer";
import {
  Panel as RPanel,
  PanelGroup,
  PanelResizeHandle,
} from "react-resizable-panels";
import { MyButton } from "./../Base/Button";
import QuestionCodeEditor from "../CodeEditor/QuestionCodeEditor";
import QuestionEngine from "../QuestionEngine/QuestionEngine";
import { useQuestionRuntime } from "../../context/QuestionAnswerContext";
import QuestionHTMLToReact from "../QuestionComponents/ParseQuestionHTML";


export function ResizableQuestionContainer() {
  const [showDevMode, setDevMode] = useState(false);
  const { showSolution, solution } = useQuestionRuntime()

  return (
    <SectionContainer
      id="questionView"
      style="primary"
      className="relative flex flex-col w-full h-full p-4 sm:p-6 
                 bg-gray-50 dark:bg-gray-900 rounded-2xl shadow-md 
                 border border-gray-200 dark:border-gray-700 transition-colors duration-200"
    >
      {/* Toolbar */}
      <div className="w-full mb-6 flex justify-end">
        <MyButton
          onClick={() => setDevMode((prev) => !prev)}
          color="primary"
          name={showDevMode ? "Close Dev Mode" : "Open Dev Mode"}
        />
      </div>

      {/* Main Resizable Panel Group */}
      <PanelGroup
        autoSaveId="conditional"
        direction="horizontal"
        className="flex w-full h-full overflow-hidden 
                   rounded-lg border border-gray-300 dark:border-gray-700"
      >
        {/* Dev Mode Panel */}
        {showDevMode && (
          <RPanel
            id="dev-mode"
            order={1}
            defaultSize={50}
            minSize={25}
            className="bg-white dark:bg-gray-800 border-r 
                       border-gray-300 dark:border-gray-700 p-4 overflow-auto"
          >
            <QuestionCodeEditor />
          </RPanel>
        )}

        {/* Solution Panel */}
        {showSolution && (
          <RPanel
            id="solution-panel"
            order={2}
            defaultSize={50}
            minSize={25}
            className="bg-white dark:bg-gray-800 border-r 
                       border-gray-300 dark:border-gray-700 p-4 overflow-auto"
          >
            <QuestionHTMLToReact html={solution} />
          </RPanel>
        )}

        {/* Resize Handle */}
        <PanelResizeHandle
          className="w-3 bg-blue-100 hover:bg-blue-400 
                     dark:bg-blue-700 dark:hover:bg-blue-600 
                     transition-colors duration-200 cursor-col-resize rounded-sm"
        />

        {/* Question Panel */}
        <RPanel
          id="question-view"
          order={3}
          defaultSize={50}
          minSize={30}
          className="flex flex-col items-center justify-center 
                     bg-white dark:bg-gray-800 p-6 overflow-auto"
        >
          <QuestionEngine />
        </RPanel>
      </PanelGroup>
    </SectionContainer>
  );
}
