import { useState } from "react";
import clsx from "clsx";
import { MyButton } from "../Base/Button";
import { MathJax } from "better-react-mathjax";

type PageRange = {
    start_page: number;
    end_page: number;
};
type Derivation = {
    derivation_title: string;
    derivation_stub: string;
    steps: string[];
    reference: PageRange;
    image?: string
};

export const derivation1: Derivation = {
    derivation_title:
        "Hydrostatic pressure in a linearly accelerating container (tilted free surface)",
    derivation_stub:
        "Show that $\\frac{dp}{dx} = -\\rho a_x$ and $\\frac{dp}{dz} = -\\rho g$; derive the free-surface slope $\\tan\\theta = \\frac{a_x}{g}$ and expressions for heights along the tank using volume conservation.",
    steps: [
        "Start from equilibrium (no relative motion in the accelerating frame): $$\\nabla p = -\\rho (\\mathbf{g} + \\mathbf{a})$$ where $\\mathbf{a}$ is the constant acceleration vector of the container. For acceleration along $x$ only ($\\mathbf{a} = a_x \\hat{i}$): $$\\frac{dp}{dx} = -\\rho a_x, \\quad \\frac{dp}{dz} = -\\rho g.$$",

        "Integrate $\\frac{dp}{dx}$: $$p(x,z) = -\\rho a_x x + f(z).$$ Integrate $\\frac{dp}{dz}$: $$f'(z) = -\\rho g \\Rightarrow f(z) = -\\rho g z + C.$$ Thus, $$p(x,z) = C - \\rho(a_x x + g z).$$",

        "On the free surface, $p = p_{atm}$ (constant). Therefore, $$p_{atm} = C - \\rho(a_x x + g z(x)),$$ giving $$z(x) = \\frac{C - p_{atm}}{\\rho g} - \\frac{a_x}{g}x.$$ The slope is $$\\frac{dz}{dx} = -\\frac{a_x}{g}, \\quad \\text{so} \\quad \\tan\\theta = \\frac{a_x}{g}.$$",

        "Use volume conservation to find the additive constant (the vertical offset of the surface). For a rectangular tank of length $L$, cross-sectional area $A$ (constant), and initial uniform depth $H_0$, require $$\\int_0^L z(x)\\,dx = H_0 L.$$",

        "With $z(x) = C' + \\frac{a_x}{g}x$ (sign chosen consistently), integrate: $$C' L + \\frac{a_x}{g}\\frac{L^2}{2} = H_0 L \\Rightarrow C' = H_0 - \\frac{a_x L}{2g}.$$",

        "Therefore, heights at $x=0$ and $x=L$ are $$H_1 = H_0 - \\frac{a_x L}{2g}, \\quad H_2 = H_0 + \\frac{a_x L}{2g},$$ and the difference is $$\\Delta H = H_2 - H_1 = \\frac{a_x L}{g}.$$"
    ],
    reference: {
        start_page: 2,
        end_page: 5,
    },
};


export function DerivationRender({
    derivation = derivation1,
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
