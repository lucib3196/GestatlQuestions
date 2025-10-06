import { useContext } from "react";
import { CodeSettings } from "./CodeSettings";
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";
import { RenderingSettings } from "./RenderingSettings";
import { QuestionStorageSettings } from "./QuestionStorageSettings";

export function QuestionSettings() {
  const {
    renderingType,
    setRenderingType,
    codeRunningSettings,
    setCodeRunningSettings,
    questionStorage,
  } = useContext(QuestionSettingsContext);

  return (
    <div
      className="mt-6 w-full rounded-xl p-6 shadow-md flex flex-col gap-6 
                 md:flex-row md:items-start md:justify-between dark:bg-surface transition-colors duration-300 bg-white-primary/20 text-primary-blue dark:text-text-primary"
    >
      {/* Code Settings */}
      <div className="flex-1">
        <h3 className="mb-2 text-lg font-semibold">
          Code Settings
        </h3>
        <CodeSettings
          language={codeRunningSettings}
          setLanguage={setCodeRunningSettings}
        />
      </div>

      {/* Rendering Settings */}
      <div className="flex-1">
        <h3 className="mb-2 text-lg font-semibold ">
          Rendering
        </h3>
        <RenderingSettings
          renderingType={renderingType}
          setRenderingType={setRenderingType}
        />
      </div>

      {/* Question Storage Settings */}
      <div className="flex-1">
        <h3 className="mb-2 text-lg font-semibold ">
          Storage
        </h3>
        <QuestionStorageSettings questionStorageType={questionStorage} />
      </div>
    </div>
  );
}