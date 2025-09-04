
import RenderAdaptiveQuestion from '../components/QuestionRendering/RenderAdaptiveQuestion';
import { RunningQuestionSettingsContext } from '../context/RunningQuestionContext';
import { useContext, useState } from 'react';
import { Panel, PanelGroup } from "react-resizable-panels";
import QuestionCodeEditor from '../components/CodeEditor/QuestionCodeEditor';
import QuestionDashBoard from './QuestionDashBoard';


function MainQuestionView() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext)
    const [editCode, setEditCode] = useState(false)

    return (
        <div className="flex flex-col items-center w-full min-h-screen bg-gray-50 py-8">
            <div className="w-full max-w-6xl flex flex-col  items-center justify-center">
                <QuestionDashBoard />
            </div>

            {selectedQuestion && (
                <div className="relative w-full justify-center flex flex-col items-center border border-gray-200 bg-white shadow-md rounded-lg mt-10 p-6">
                    <div className="flex flex-row gap-4 mb-6">
                        <button
                            className="px-5 py-2 rounded-md bg-indigo-500 text-white font-semibold shadow hover:bg-indigo-600 transition"
                            onClick={() => setEditCode((prev) => !prev)}
                        >
                            Edit Code
                        </button>
                        <button
                            className="px-5 py-2 rounded-md bg-green-500 text-white font-semibold shadow hover:bg-green-600 transition"
                            disabled={true}
                        >
                            Submit Review
                        </button>

                    </div>
                    <div className="w-full">
                        <PanelGroup autoSaveId="conditional" direction="horizontal">
                            {editCode && <Panel
                                id="code_editor"
                                order={1}>
                                <div className=' w-full h-full'>
                                    <QuestionCodeEditor />
                                </div>
                            </Panel>}
                            <Panel id="question" order={2}>
                                <RenderAdaptiveQuestion />
                            </Panel>

                        </PanelGroup>


                    </div>
                </div>
            )}

        </div>
        // 

    )
}


export default MainQuestionView