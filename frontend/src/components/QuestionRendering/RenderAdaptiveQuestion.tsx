import { useContext } from "react";
import { QuestionSettingsContext } from './../../context/GeneralSettingsContext';
import { LegacyQuestion } from "./LegacyQuestion";
import { NewQuestion } from "./NewQuestion";
/**
 * Top-level wrapper: chooses legacy vs new rendering.
 */
export default function RenderAdaptiveQuestion() {
    const { renderingSettings } = useContext(QuestionSettingsContext);

    return (
        <div className="flex flex-col items-center justify-center w-full px-4 py-6">
            {renderingSettings === "legacy" ? <LegacyQuestion /> : <NewQuestion />}
        </div>
    );
}