import { useContext } from "react";
import { QuestionSettingsContext } from './../../context/GeneralSettingsContext';
import { LegacyQuestion } from "../QuestionView/LegacyQuestion";
import { NewQuestion } from "./NewQuestion";
import { MathJax } from "better-react-mathjax";
/**
 * Top-level wrapper: chooses legacy vs new rendering.
 */
export default function RenderAdaptiveQuestion() {
    const { renderingType } = useContext(QuestionSettingsContext);

    return (
        <div className="flex flex-col items-center justify-center  w-max-9/10 px-4 py-6">
            {renderingType === "legacy" ? <LegacyQuestion /> : <NewQuestion />}
        </div>

    );
}