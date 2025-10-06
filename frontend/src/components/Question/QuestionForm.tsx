import type { Question } from "../../types/questionTypes"
import type { JSX } from "react";

type Renderer<T> = Partial<
    { [K in keyof T]: (
        value: T[K],
        onChange: (v: T[K]) => void
    ) => JSX.Element }
>;

export const questionRenderer: Renderer<Question> = {
    title: (value, onChange) => (
        <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
        />
    ),
    topics: (value, onChange) => (
        <div>
            {value.map((v, i) => (
                <input
                    key={i}
                    type="text"
                    value={v}
                    onChange={(e) => {
                        const newTopics = [...value];
                        newTopics[i] = e.target.value;
                        onChange(newTopics);
                    }}
                />
            ))}
        </div>
    ),
    languages: (value, onChange) => (
        <div>
            {value.map((v, i) => (
                <input
                    key={i}
                    type="text"
                    value={v}
                    onChange={(e) => {
                        const newLanguages = [...value];
                        newLanguages[i] = e.target.value;
                        onChange(newLanguages);
                    }}
                />
            ))}
        </div>
    ),
    qtypes: (value, onChange) => (
        <div>
            {value.map((v, i) => (
                <input
                    key={i}
                    type="text"
                    value={v}
                    onChange={(e) => {
                        const newQTypes = [...value];
                        newQTypes[i] = e.target.value;
                        onChange(newQTypes);
                    }}
                />
            ))}
        </div>
    ),
    isAdaptive: (value, onChange) => (
        <input
            type="checkbox"
            checked={value}
            onChange={(e) => onChange(e.target.checked)}
        />
    ),
    ai_generated: (value, onChange) => (<input
        type="checkbox"
        checked={value}
        onChange={(e) => onChange(e.target.checked)}
    />)
    ,

};



