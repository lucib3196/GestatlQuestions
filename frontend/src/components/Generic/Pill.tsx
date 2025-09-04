


type PillProps = {
    content: string;
    textColor?: string;
    bgColor?: string;
};

const Pill: React.FC<PillProps> = ({ content, textColor, bgColor }) => {
    return (
        <div className={`flex items-center px-3 py-1 rounded-full  text-sm font-medium shadow-sm $
            ${textColor ? textColor : " text-blue-800"}
            ${bgColor ? bgColor : "bg-blue-100"}`
        }>
            {content}
        </div>
    );
};

export default Pill