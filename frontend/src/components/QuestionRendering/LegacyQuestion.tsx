import { useEffect, useRef, useContext, useState } from "react";
import { RunningQuestionSettingsContext } from "../../context/RunningQuestionContext";
import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";
import api from "../../api";
import * as plutil from "../../legacy/plutil.js"
import { processPrairielearnTags } from "../../legacy/readPrairielearn.js";

export function LegacyQuestion() {
    const { selectedQuestion } = useContext(RunningQuestionSettingsContext);
    const { codeRunningSettings } = useContext(QuestionSettingsContext);
    const [legacyHTML, setLegacyHTML] = useState("");
    const htmlRef = useRef<HTMLDivElement>(null);
    const choiceParams = { fracQuestions: [1.0, 1.0] }; // Not sure what this is 

    useEffect(() => {
        if (!selectedQuestion) return;
        (async () => {
            try {
                const [htmlRes, paramsRes] = await Promise.all([
                    api.get(`/local_questions/get_question_html/${selectedQuestion}`),
                    api.get(`/local_questions/get_server_data/${selectedQuestion}/${codeRunningSettings}`)
                ]);
                let content = htmlRes.data as string;
                // adapt mustache syntax
                content = content.replaceAll("[[", "{{").replaceAll("]]", "}}");
                const paramData = paramsRes.data.quiz_response;
                // replace and process tags
                console.log(content)
                console.log(paramData)
                const replaced = plutil.replace_params(content, paramData);
                const { htmlString } = processPrairielearnTags(replaced, paramData, "", "", choiceParams);
                setLegacyHTML(htmlString);
            } catch (err) {
                console.error("Failed to load legacy question", err);
            }
        })();
    }, [selectedQuestion, codeRunningSettings]);

    // trigger MathJax render
    useEffect(() => {
        if ((window as any).MathJax && htmlRef.current) {
            (window as any).MathJax.typesetPromise([htmlRef.current]).catch(console.error);
        }
    }, [legacyHTML]);

    return (
        <div className="w-full max-w-6xl bg-white shadow-lg p-9 rounded-lg">
            <div ref={htmlRef} dangerouslySetInnerHTML={{ __html: legacyHTML }} />
        </div>
    );
}