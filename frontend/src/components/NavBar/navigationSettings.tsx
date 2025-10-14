// React Router
import { Route } from "react-router-dom";

// Types
import { QuestionViewPage } from "../../pages/QuestionsPage";
import ImageGenerator from "../CodeGenerators/ImageGenerator";
import TextGenerator from "../CodeGenerators/TextGenerator";
import Home from "../../pages/Home";
import type { navigationType } from "../../types/navbarTypes";

export const navigation: navigationType[] = [
    {
        name: "Home",
        href: "/",
        element: <Home />,
        current: false,
        requiresAccount: false,
        includeNavbar: false
    },
    {
        name: "Home",
        href: "/home",
        element: <Home />,
        current: false,
        requiresAccount: false,
        includeNavbar: true
    },
    {
        name: "Questions",
        href: "/questions",
        element: <QuestionViewPage />,
        current: false,
        requiresAccount: false,
        includeNavbar: true
    },
    // {
    //     name: "Create Question",
    //     href: "/createQuestion",
    //     element: <CreateQuestionPage />,
    //     current: false,
    //     requiresAccount: false,
    //     includeNavbar: true
    // },
    {
        name: "Generators",
        href: "/generators",
        current: false,
        requiresAccount: true,
        includeNavbar: true,
        dropdown: true,
        dropdownItems: [
            {
                name: "Text",
                href: "/generators/text_generator",
                element: <TextGenerator />,
            },
            {
                name: "ImageUpload",
                href: "/generators/image_generator",
                element: <ImageGenerator />,
            },
        ],
    },
];

export function handleRoutes(navigation: navigationType[]) {
    return navigation.map((nav) =>
        nav.dropdown ? (
            nav.dropdownItems?.map((dI) => (
                <Route path={dI.href} element={dI.element}></Route>
            ))
        ) : (
            <Route path={nav.href} element={nav.element}></Route>
        )
    );
}
