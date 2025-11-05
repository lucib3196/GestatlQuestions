import { useQuestionContext } from "../../context/QuestionContext"
import type { QuestionMeta } from "../../types/questionTypes"


function QuestionFormHeader({ questionMeta }: { questionMeta: QuestionMeta }) {
    return (<div>
        <h1>Question: {questionMeta.title}</h1>
    </div>)
}
export default function QuestionUpdateForm() {
    const { questionMeta, selectedQuestionID } = useQuestionContext()

    console.log("This is the question metat", selectedQuestionID)

    if (!questionMeta) {
        return null
    }

    return <div>
        <QuestionFormHeader questionMeta={questionMeta} />

    </div>
}