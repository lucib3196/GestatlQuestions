

export type PLQuestionPanelProps = {
    children?: any
}
const PLQuestionPanel = ({ children }: PLQuestionPanelProps) => (
    <div className="border flex items-center text-center  p-4 min-w-[300px] min-h-[400px] rounded-md">{children}
    </div>
);

export default PLQuestionPanel