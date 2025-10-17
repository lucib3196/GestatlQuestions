
import { CiCircleQuestion } from "react-icons/ci"
import type { IconType } from "react-icons/lib";
import { useState } from "react"

type HelperPopUpProps = {
    value: string;
    variant?: "top" | "bottom" | "left" | "right";

};
type HelperPopUpIconProps = HelperPopUpProps & {
    icon?: IconType;
    onClick?: () => void
};

export function PopUpHelper({ value, variant = "top" }: HelperPopUpProps) {
    const baseStyle =
        "absolute w-64 p-3 text-sm rounded-lg shadow-lg z-50 bg-white text-black dark:bg-gray-900 dark:text-gray-100 transition-all duration-200";

    const positionStyles: Record<typeof variant, string> = {
        top: "bottom-full mb-2 left-1/2 -translate-x-1/2",
        bottom: "top-full mt-2 left-1/2 -translate-x-1/2",
        left: "right-full mr-2 top-1/2 -translate-y-1/2",
        right: "left-full ml-2 top-1/2 -translate-y-1/2",
    };

    return (
        <div className={`${baseStyle} ${positionStyles[variant]}`}>
            {value}
        </div>
    );
}


export const PopUpHelpIcon: React.FC<HelperPopUpIconProps> = ({
    value,
    variant = "top",
    icon: Icon = CiCircleQuestion, 
    onClick
}) => {
    const [showMessage, setShowMessage] = useState(false);

    const baseClasses =
        "absolute border rounded-md w-[100px] sm:w-[150px] break-words whitespace-pre-wrap px-4 py-2 text-sm shadow-md transition-all duration-200 z-50 " +
        "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100";

    const variantClasses: Record<NonNullable<typeof variant>, string> = {
        top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
        bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
        left: "right-full top-1/2 -translate-y-1/2 mr-2",
        right: "left-full top-1/2 -translate-y-1/2 ml-2",
    };

    return (
        <div className="relative inline-block" role="tooltip">
            <Icon
                size={20}
                className="text-gray-600 dark:text-gray-300 cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150"
                onMouseEnter={() => setShowMessage(true)}
                onMouseLeave={() => setShowMessage(false)}
                onClick={onClick}
            />
            {showMessage && (
                <div className={`${baseClasses} ${variantClasses[variant]}`}>
                    {value}
                </div>
            )}
        </div>
    );
};