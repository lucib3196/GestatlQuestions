import { MathJax } from "better-react-mathjax";

// --- Render HTML with MathJax ---
type QuestionHtmlProps = {
    html: string;
};

export const QuestionHtml: React.FC<QuestionHtmlProps> = ({ html }) => (
    <MathJax>
        <div
            className={`
        prose prose-sm sm:prose-base lg:prose-lg
        max-w-none w-full
        mt-6
        text-inherit
        leading-relaxed
        dark:prose-invert
        [&>*]:my-4
      `}
            dangerouslySetInnerHTML={{ __html: html }}
        />
    </MathJax>
);