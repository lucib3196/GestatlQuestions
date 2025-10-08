import SectionContainer from "../components/Base/SectionContainer";
import { MyButton } from "../components/Base/Button";
import { HashLink } from "react-router-hash-link";
import { GeneratorContainer } from "../components/CodeGenerators/AIGeneratorBox";
import Card from "../components/Base/Card";
import { Link } from "react-router-dom";
function Hero() {
    return (
        <SectionContainer id="hero" style="hero" className="bg-gray-50 dark:bg-gray-900">
            <div className="text-center space-y-6 px-6 max-w-3xl mx-auto py-20">
                {/* Title */}
                <h1 className="font-extrabold text-4xl sm:text-6xl text-gray-900 dark:text-white">
                    Gestalt Generator
                    Hello some change i did 
                </h1>

                <hr className="border-primary-yellow dark:border-primary-yellow/70 w-24 mx-auto" />

                {/* Subtitle */}
                <h2 className="font-semibold text-lg sm:text-2xl italic text-primary-yellow">
                    Empowering Educators with AI-Powered STEM Content Creation
                </h2>

                {/* Call to Action */}
                <HashLink smooth to="/home/#about">
                    <MyButton
                        name="Get Started"
                        variant="third"
                        className="px-8 py-4 mt-6 rounded-2xl text-xl sm:text-2xl font-extrabold shadow-lg hover:scale-105 transition-transform"
                    />
                </HashLink>
            </div>
        </SectionContainer>
    );
}

function AboutSection() {
    return (
        <SectionContainer id="about" style="hero" className="bg-white dark:bg-gray-800">
            <div className="max-w-4xl mx-auto text-center space-y-8 px-6 py-16">
                {/* Heading */}
                <h2 className="text-3xl sm:text-5xl font-extrabold text-gray-900 dark:text-white">
                    About Gestalt Generator
                </h2>

                <hr className="border-primary-yellow dark:border-primary-yellow/70 w-20 mx-auto" />

                {/* Description */}
                <div className="space-y-6 max-w-prose mx-auto">
                    <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 leading-relaxed">
                        Gestalt Generator is an AI-powered platform designed to{" "}
                        <span className="font-semibold text-primary-yellow">help educators</span>{" "}
                        create high-quality STEM learning content with ease.
                    </p>

                    <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 leading-relaxed">
                        Whether you’re working with{" "}
                        <span className="italic">single questions, full lecture notes, or scanned documents</span>,
                        our tools transform raw material into{" "}
                        <span className="font-semibold">
                            step-by-step solution guides, adaptive modules, and interactive practice problems
                        </span>.
                    </p>
                </div>

                <HashLink smooth to="/home/#how-it-works">
                    <MyButton
                        name="How It Works"
                        variant="primary"
                        className="px-6 py-3 rounded-xl text-lg font-bold shadow hover:scale-105 transition-transform"
                    />
                </HashLink>
            </div>
        </SectionContainer>
    );
}

function GeneratorSection() {
    return (
        <SectionContainer id="generator-section" style="hero" className="bg-gray-50 dark:bg-gray-900">
            <div className="flex flex-col items-center justify-center space-y-10 py-20">
                <GeneratorContainer />
                <HashLink smooth to="#learn-more">
                    <MyButton
                        name="Learn More"
                        variant="secondary"
                        className="px-6 py-3 rounded-xl text-lg sm:text-xl font-bold shadow-md hover:scale-105 transition-transform"
                    />
                </HashLink>
            </div>
        </SectionContainer>
    );
}

function LearnMore() {
    return (
        <SectionContainer id="learn-more" style="hero" className="bg-white dark:bg-gray-800">
            <div className="max-w-6xl mx-auto text-center space-y-10 px-6 py-16">
                {/* Heading */}
                <h2 className="text-3xl sm:text-5xl font-extrabold text-gray-900 dark:text-white">
                    Learn More: Behind the Scenes
                </h2>

                <hr className="border-primary-yellow dark:border-primary-yellow/70 w-20 mx-auto" />

                {/* Intro */}
                <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 leading-relaxed max-w-3xl mx-auto">
                    Our system combines{" "}
                    <span className="font-semibold text-primary-yellow">Large Language Models (LLMs)</span>{" "}
                    with{" "}
                    <span className="font-semibold text-primary-yellow">Retrieval-Augmented Generation (RAG)</span>{" "}
                    to ensure accuracy, context, and adaptability.
                </p>

                {/* Steps with cards */}
                <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
                    {[
                        {
                            step: "1",
                            title: "Document Upload",
                            text: "Upload a text question, scanned image, or lecture notes. Content is preprocessed into structured data chunks."
                        },
                        {
                            step: "2",
                            title: "Embedding Creation",
                            text: "The text is transformed into vector embeddings that capture meaning, enabling semantic search instead of keyword matching."
                        },
                        {
                            step: "3",
                            title: "RAG-Based Retrieval",
                            text: "Relevant examples, code snippets, and prior solutions are retrieved and injected as context into the LLM."
                        },
                        {
                            step: "4",
                            title: "AI Module Generation",
                            text: "The LLM combines retrieved context with input to generate step-by-step solutions, executable code, and metadata."
                        }
                    ].map((item) => (
                        <Card
                            key={item.step}
                            className="justify-start bg-gray-100 dark:bg-gray-900 shadow-md rounded-xl p-6 text-left hover:shadow-lg transition  items-start"
                        >
                            <div className="text-3xl font-extrabold text-primary-yellow">{item.step}</div>
                            <h3 className="font-bold text-lg text-gray-900 dark:text-white mt-2">
                                {item.title}
                            </h3>
                            <p className="text-gray-700 dark:text-gray-300 mt-2">{item.text}</p>
                        </Card>
                    ))}
                </div>

                {/* Closing summary */}
                <p className="text-lg text-gray-700 dark:text-gray-300 max-w-3xl mx-auto mt-10">
                    By pairing retrieval with generation, Gestalt Generator ensures modules are{" "}
                    <span className="font-semibold text-primary-yellow">accurate, contextual, and ready to use</span>.
                </p>
            </div>
        </SectionContainer>
    );
}

function HowItWorks() {
    return (
        <SectionContainer id="how-it-works" style="hero" className="bg-gray-50 dark:bg-gray-900">
            <div className="max-w-5xl w-full mx-auto text-center space-y-10 px-6 py-16">
                {/* Heading */}
                <h2 className="text-3xl sm:text-5xl font-extrabold text-gray-900 dark:text-white">
                    How It Works
                </h2>

                <hr className="border-primary-yellow dark:border-primary-yellow/70 w-20 mx-auto" />

                {/* Steps */}
                <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-2">
                    {[
                        {
                            step: "1",
                            title: "Choose Your Input",
                            text: "Start with a single question, scanned notes, or lecture slides—whatever fits your workflow."
                        },
                        {
                            step: "2",
                            title: "Pick a Generator",
                            text: "Select QuickQuery, VisualExtract, or LectureInsight based on whether you’re working with text, images, or full lectures."
                        },
                        {
                            step: "3",
                            title: "Get Instant Modules",
                            text: "Receive practice-ready modules that include step-by-step guides, code, and interactive elements."
                        },
                        {
                            step: "4",
                            title: "Review & Customize",
                            text: "Adjust content, add your own questions, and download files to fit your course or study style."
                        }
                    ].map((item) => (
                        <Card
                            key={item.step}
                            className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 text-left hover:shadow-lg transition"
                        >
                            <div className="text-sm sm:text-3xl font-extrabold text-primary-yellow">{item.step}</div>
                            <h3 className="text-sm font-bold sm:text-lg text-gray-900 dark:text-white mt-2">
                                {item.title}
                            </h3>
                            <p className="text-sm text-gray-700 dark:text-gray-300 mt-2 sm:text-sm">{item.text}</p>
                        </Card>
                    ))}
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-6 justify-center pt-6">
                    <HashLink smooth to="/home/#generator-section">
                        <MyButton
                            name="Start with Generators"
                            variant="primary"
                            className="px-6 py-3 rounded-xl text-lg font-bold shadow hover:scale-105 transition-transform"
                        />
                    </HashLink>
                    <HashLink smooth to="#questions">
                        <MyButton
                            name="Explore Questions"
                            variant="secondary"
                            className="px-6 py-3 rounded-xl text-lg font-bold shadow-md hover:scale-105 transition-transform"
                        />
                    </HashLink>
                </div>
            </div>
        </SectionContainer>
    );
}
function QuestionsSection() {
    return (
        <SectionContainer id="questions" style="hero" className="bg-gray-50 dark:bg-gray-900">
            <div className="max-w-5xl mx-auto text-center space-y-10 px-6 py-16">
                {/* Heading */}
                <h2 className="text-3xl sm:text-5xl font-extrabold text-gray-900 dark:text-white">
                    Explore Questions
                </h2>

                <hr className="border-primary-yellow dark:border-primary-yellow/70 w-20 mx-auto" />

                {/* Intro */}
                <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 leading-relaxed max-w-3xl mx-auto">
                    Beyond generating modules, you can{" "}
                    <span className="font-semibold text-primary-yellow">explore existing  questions </span>
                    in the Question Page. See examples, review solutions, and reuse modules to speed up your workflow.
                </p>

                {/* Features */}
                <div className="grid gap-8 sm:grid-cols-2">
                    <Card className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 hover:shadow-lg transition text-left">
                        <h3 className="font-bold text-xl text-gray-900 dark:text-white mb-2">
                            Browse Generated Questions
                        </h3>
                        <p className="text-gray-700 dark:text-gray-300">
                            Access a library of already-generated questions, complete with solutions and module files — ready to test or adapt.
                        </p>
                    </Card>

                    <Card className="bg-white dark:bg-gray-800 shadow-md rounded-xl p-6 hover:shadow-lg transition text-left">
                        <h3 className="font-bold text-xl text-gray-900 dark:text-white mb-2">
                            Create Manual Questions
                        </h3>
                        <p className="text-gray-700 dark:text-gray-300">
                            For full flexibility, manually create your own questions and customize them to fit your exact needs.
                        </p>
                    </Card>
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row justify-center gap-6 pt-8">

                    <Link to="/questions">
                        <MyButton
                            name="Go to Question Page"
                            variant="primary"
                            className="px-6 py-3 rounded-xl text-lg font-bold shadow hover:scale-105 transition-transform"
                        />
                    </Link>
                    <Link to="/createQuestion">"
                        <MyButton
                            name="Create Manual Question"
                            variant="secondary"
                            className="px-6 py-3 rounded-xl text-lg font-bold shadow hover:scale-105 transition-transform"
                        />
                    </Link>

                </div>
            </div>
        </SectionContainer>
    );
}


export default function Home() {
    return (
        <>
            <Hero />
            <AboutSection />
            <HowItWorks />
            <GeneratorSection />
            <QuestionsSection />
            <LearnMore />

        </>
    );
}
