import { useState } from "react";
import clsx from "clsx";
import { MyButton } from "../Base/Button";
import { MathJax } from "better-react-mathjax";

type PageRange = {
    start_page: number;
    end_page: number;
};
export type Derivation = {
    derivation_title: string;
    derivation_stub: string;
    steps: string[];
    reference: PageRange;
    image?: string
};




export function DerivationRender({
    derivation,
}: {
    derivation: Derivation;
}) {
    const [stepID, setStepID] = useState<number>(-1);

    return (
        <MathJax className="">
            <div className="w-8/10 mx-auto p-8 bg-white rounded-xl shadow-md border border-gray-200 flex flex-col min-h-[70vh] max-h-[90vh] ">
                {/* Fixed Header Section */}
                <div className="text-center pb-4 border-b border-gray-200">
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                        {derivation.derivation_title}
                    </h1>
                    <p className="text-gray-600 mt-3 text-base italic leading-relaxed">
                        {derivation.derivation_stub}
                    </p>
                </div>

                {/* Scrollable Steps Section */}
                <div className="flex-1 overflow-y-auto mt-6 pr-2 space-y-6">
                    {derivation.steps.map((step, idx) => (
                        <div
                            key={idx}
                            className={clsx(
                                "transition-all duration-300 ease-in-out transform",
                                idx <= stepID
                                    ? "opacity-100 translate-y-0"
                                    : "opacity-0 -translate-y-2 hidden"
                            )}
                        >
                            <div className="p-4 bg-gray-50 border-l-4 border-blue-500 rounded-md shadow-sm">
                                <p className="text-gray-800 leading-relaxed text-[15px] sm:text-base">
                                    <span className="font-semibold text-blue-700">
                                        Step {idx + 1}:
                                    </span>{" "}
                                    {step}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Button Section (sticky footer) */}
                <div className="mt-6 pt-4 border-t border-gray-200 flex justify-end">
                    <MyButton
                        name={
                            stepID >= derivation.steps.length - 1
                                ? "Restart Derivation"
                                : "Show Next Step"
                        }
                        onClick={() =>
                            setStepID((prevStep) =>
                                prevStep < derivation.steps.length - 1 ? prevStep + 1 : -1
                            )
                        }
                    />
                </div>
            </div>
        </MathJax>
    );
}
