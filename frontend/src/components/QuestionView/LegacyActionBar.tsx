import {
    GenerateNewVariantButton,
    ResetQuestionButton,
    ShowSolutionStep,
    SubmitAnswerButton,
} from "../Generic/Buttons";
import type { FormEvent } from "react";


const ActionBar: React.FC<{
    onSubmit: (e: FormEvent) => void;
    onReset: () => void;
    onVariant: () => void;
    onToggleSolution: () => void;
    disabledSubmit: boolean;
    disabledReset: boolean;
    disabledVariant: boolean;
    showSolution: boolean;
}> = ({
    onSubmit,
    onReset,
    onVariant,
    onToggleSolution,
    disabledSubmit,
    disabledReset,
    disabledVariant,
    showSolution,
}) => (
        <div className="mt-6 bg-white border border-slate-200 rounded-xl shadow-sm p-4">
            <div className="flex flex-wrap items-center gap-3 justify-center">
                <form onSubmit={onSubmit}>
                    <SubmitAnswerButton disabled={disabledSubmit} />
                </form>
                <ResetQuestionButton onClick={onReset} disabled={disabledReset} />
                <GenerateNewVariantButton onClick={onVariant} disabled={disabledVariant} />
                <ShowSolutionStep onClick={onToggleSolution} disabled={false} showSolution={showSolution} />
            </div>
        </div>
    );

export default ActionBar