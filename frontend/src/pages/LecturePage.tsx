import { DerivationRender } from "../components/LectureComponents/Derivation";
import SectionContainer from "../components/Base/SectionContainer";
import type { Derivation } from "../components/LectureComponents/Derivation";

const mock_data: Derivation = {
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
export function LecturePage(){
    return (
        <SectionContainer id="derivation" >
        <DerivationRender derivation={mock_data}/>
        </SectionContainer>
    )
}