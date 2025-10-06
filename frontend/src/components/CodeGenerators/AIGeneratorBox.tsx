import Card from "../Base/Card";
import { MyButton } from "../Base/Button";
import { generators } from "./generatorInfo";
import type { GeneratorConfig } from "./generatorInfo";
import { Link } from "react-router-dom";

type AIGeneratorBoxProps = {
    config: GeneratorConfig
}


function AIGeneratorBox({ config }: AIGeneratorBoxProps) {
    return (
        <Card className="flex-1 min-w-[250px] min-h-[200px]">
            <h1 className="text-lg font-bold">{config.name}</h1>
            <p className="text-sm ">{config.description}</p>
            <Link to={config.link}>
                <MyButton name={config.name} className="mt-10" ></MyButton>
            </Link>
        </Card>
    )
}

export function TextGeneratorBox() {
    return <AIGeneratorBox config={generators.text} />
}

export function ImageGeneratorBox() {
    {
        return <AIGeneratorBox config={generators.image} />
    }
}
export function LectureSummary() {
    return <AIGeneratorBox config={generators.lecture} />
}
export function GeneratorContainer() {
    return (
        <div className="max-w-8/10  mx-auto flex flex-col items-center text-center">
            <h2 className="text-xl sm:text-3xl md:text-4xl font-extrabold text-gray-800 dark:text-white mb-6">
                Try Our AI Generators for Creating Questions
            </h2>
            <p className="text-gray-600 dark:text-gray-300 max-w-2xl mb-10">
                Choose between text-based or image-based generation to create practice modules
                tailored for students.
            </p>

            <div className="flex flex-row flex-wrap justify-center gap-2 w-full gap-x-10 gap-y-5">
                <TextGeneratorBox />
                <ImageGeneratorBox />
                <LectureSummary />
            </div>
        </div>
    )
}