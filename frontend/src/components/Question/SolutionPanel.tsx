import { MathJax } from "better-react-mathjax";
import Markdown from "react-markdown";
import remarkBreaks from "remark-breaks";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import rehypeMathjax from "rehype-mathjax";

import Panel from "../Base/Panel";

type SolutionPanelProps = {
    title?: string;
    subtitle?: string;
    solution: Array<string> | Array<React.ReactNode>;
};

type SolutionListProps = {
    solution: string[] | Array<React.ReactNode>;
};

export function SolutionList({ solution }: SolutionListProps) {
    return (
        <ol className="space-y-6">
            {solution.map((val, index) => (
                <li key={index} className="relative flex gap-4">
                    {/* Step number */}
                    <div className="flex h-8 w-8 flex-none items-center justify-center rounded-full border border-indigo-200 bg-indigo-50 text-sm font-semibold text-indigo-700 dark:border-indigo-600 dark:bg-indigo-900 dark:text-indigo-100">
                        {index + 1}
                    </div>

                    {/* Step content */}
                    <div className="prose prose-indigo dark:prose-invert max-w-none">
                        <Markdown
                            remarkPlugins={[remarkGfm, remarkBreaks]}
                            rehypePlugins={[rehypeRaw, rehypeMathjax]}
                            components={{
                                p: ({ children }) => (
                                    <p className="m-0 whitespace-pre-line">{children}</p>
                                ),
                            }}
                        >
                            {typeof val === "string" ? val.trim() : String(val)}
                        </Markdown>
                    </div>
                </li>
            ))}
        </ol>
    );
}

export function SolutionPanel({
    title = "Solution",
    subtitle,
    solution,
}: SolutionPanelProps) {
    return (
        <MathJax>
            <Panel >
                {/* Header */}
                <div>
                    <h2 className="text-xl sm:text-2xl font-semibold">{title}</h2>
                    {subtitle && (
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            {subtitle}
                        </p>
                    )}
                </div>

                {/* Solution Steps */}
                <div className="mt-4">
                    <SolutionList solution={solution} />
                </div>

                {/* Footer Note */}
                <div className="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4 text-center text-xs text-gray-500 dark:text-gray-400">
                    Review each step before proceeding.
                </div>
            </Panel>
        </MathJax>
    );
}

