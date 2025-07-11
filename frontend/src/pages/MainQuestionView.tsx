
import { QuestionFilter } from './../components/QuestionViews/QuestionFilter';
import LocalQuestionsView from '../components/QuestionViews/LocalQuestions';
import RenderAdaptiveQuestion from '../components/QuestionRendering/RenderAdaptiveQuestion';
import { RunningQuestionSettingsContext } from '../context/RunningQuestionContext';
import { useContext } from 'react';
function MainQuestionView() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext)

    return (
        <div className="flex flex-col justify-center items-center">
            <QuestionFilter />
            <LocalQuestionsView />
            {selectedQuestion && <RenderAdaptiveQuestion></RenderAdaptiveQuestion>}

        </div>
    )
}


export default MainQuestionView