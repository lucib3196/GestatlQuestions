
import clsx from "clsx";


type TableToolBarProps = {
    value: string;
    onClick: () => void;
    disabled?: boolean;
    className: string;
    disabledClassName?: string;
    onHoverMsg?: string;
    icon?: React.ReactNode;
};

export const TableToolBarButton = ({
    value,
    onClick,
    disabled = false,
    className,
    disabledClassName = "border-gray-300 text-gray-400 cursor-not-allowed",
    onHoverMsg,
    icon,
}: TableToolBarProps) => {
    return (
        <button
            type="button"
            title={onHoverMsg}
            onClick={onClick}
            className={clsx(
                "border-2 px-3 py-2 rounded-md transition",

                className, // always apply the base className
                disabled && disabledClassName, // only apply if disabled
                icon && "display flex flex-row gap-2"
            )}
            disabled={disabled}
        >
            {icon} {value}
        </button>
    );
};
