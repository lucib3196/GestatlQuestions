import React from "react";

// 📌 Interfaces
interface ExampleItem {
    name: string;
    text: string;
}

interface ModGeneratorProps {
    title: string;
    subtitle: string;
    examples: ExampleItem[];
    inputComponent?: React.ReactNode | React.FC
}

interface ModInfoProps {
    title: string;
    subtitle: string;
}

interface IndividualExample {
    example: string;
    name?: string;
    index: number;
}

// 📘 Components

// Renders title and subtitle
const ModInfo: React.FC<ModInfoProps> = ({ title, subtitle }) => (
    <div className="flex flex-col items-center mt-6 mb-4 px-4 text-center">
        <h1 className="text-4xl font-extrabold text-DarkShades mb-2 leading-tight break-words">
            {title}
        </h1>
        <h2 className="text-xl font-semibold text-blue-500 mt-1 max-w-2xl">
            {subtitle}
        </h2>
        <div className="w-16 h-1 bg-blue-200 rounded-full mt-3 mb-1" />
    </div>
);

// Renders a single example
const IndividualExampleContainer: React.FC<IndividualExample> = ({
    example,
    index,
    name,
}) => (
    <div className="flex flex-col mb-4 w-full bg-blue-50 rounded-lg p-4 shadow-sm border border-blue-100">
        <div className="flex items-center mb-2">
            <span className="text-blue-700 font-semibold mr-2">
                Example {index}
            </span>
            {name && (
                <span className="text-gray-500 italic text-sm">- {name}</span>
            )}
        </div>
        <p className="ml-2 leading-relaxed text-base text-DarkShades italic">{example}</p>
    </div>
);

// Renders the full example list
const ModExample: React.FC<{ examples: ExampleItem[] }> = ({ examples }) => (
    <>
        <h3 className="text-lg font-semibold italic text-LightAccent mb-2">The following are examples of valid inputs</h3>
        <div className="flex justify-center w-full mt-4">
            <ul className="w-full list-none p-0">
                {examples.map((example, index) => (
                    <li key={index} className="ind-ex-container">
                        <IndividualExampleContainer
                            example={example.text}
                            name={example.name}
                            index={index + 1}
                        />
                    </li>
                ))}
            </ul>
        </div>
    </>
);

// Top-level generator component
const ModGenerators: React.FC<ModGeneratorProps> = ({
    title,
    subtitle,
    examples,
    inputComponent
}) => (
    <div className="flex flex-col items-center my-6 mx-auto border border-gray-200 rounded-2xl max-w-7/10 min-w-[350px] p-8 bg-white shadow-lg">
        <ModInfo title={title} subtitle={subtitle} />
        <div className="w-full mt-4 flex flex-col">
            <ModExample examples={examples} />
        </div>
        {inputComponent && (
            <div className="w-full mt-6 flex">
                {typeof inputComponent === "function"
                    ? React.createElement(inputComponent)
                    : inputComponent}
            </div>
        )}
    </div>
);



export default ModGenerators;
