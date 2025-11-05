

export type PLQuestionPanelProps = {
    children?: any
}
const PLQuestionPanel = ({ children }: PLQuestionPanelProps) => (
    <div className="border flex text-center  p-4 min-w-[300px] min-h-[400px] rounded-md">{children}
    
    <p className="text-2xl font-bold hidden">Correct answer</p></div>
);

export default PLQuestionPanel