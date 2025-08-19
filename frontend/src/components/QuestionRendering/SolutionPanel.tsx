import { MathJax } from "better-react-mathjax";
import type { ReactNode } from "react";
import Markdown from "react-markdown";
import remarkBreaks from 'remark-breaks'
import remarkGfm from 'remark-gfm'
import rehypeRaw from "rehype-raw";
import rehypeMathjax from "rehype-mathjax";
type SolutionPanelProps = {
    title?: string;
    subtitle?: string;
    solution: Array<string | ReactNode>;
};

export function SolutionPanel({ title = "Solution", subtitle, solution }: SolutionPanelProps) {
    if (!solution?.length) return null;

    console.log("This is the solutio", solution)

    return (
        <section className="mx-auto my-10 w-full max-w-3xl rounded-2xl border border-gray-200 bg-white p-6 shadow-md transition-shadow hover:shadow-lg">
            {/* Header */}
            <header className="mb-6 text-center">
                <h2 className="text-2xl font-semibold tracking-tight text-gray-900">{title}</h2>
                {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
            </header>

            {/* Steps */}
            <ol className="space-y-5">
                {solution.map((value, idx) => (
                    <li key={idx} className="relative flex gap-4">
                        {/* Step bullet */}
                        <div className="flex h-8 w-8 flex-none items-center justify-center rounded-full border border-indigo-200 bg-indigo-50 text-sm font-semibold text-indigo-700">
                            {idx + 1}
                        </div>

                        {/* Content */}

                        <div className="min-w-0 flex-1">
                            <MathJax>
                                <div className="prose prose-indigo max-w-none text-gray-800">
                                    {typeof value === "string" ? (
                                        // supports **bold**, _italics_, `code`, lists, etc.
                                        <Markdown remarkPlugins={[remarkGfm, remarkBreaks]}
                                            rehypePlugins={[rehypeRaw, rehypeMathjax]}
                                            components={{
                                                p: ({ children }) => <p className="m-0 whitespace-pre-line">{children}</p>,
                                            }}
                                        >
                                            {value.trim()}
                                        </Markdown>
                                    ) : (
                                        value
                                    )}
                                </div>
                            </MathJax>
                        </div>

                    </li>
                ))}
            </ol>

            {/* Footer divider */}
            <div className="mt-6 border-t border-gray-100 pt-4 text-center text-xs text-gray-500">
                Review each step before proceeding.
            </div>

        </section>
    );
}