import clsx from "clsx";

type CardVarientType = "primary" | "secondary";

const cardStyles: Record<CardVarientType, string> = {
    primary: "",
    secondary: "",
};

type CardProps = {
    children: React.ReactNode;
    className?: string;
    varient?: CardVarientType;
};

export default function Card({
    children,
    className = "",
    varient = "primary",
}: CardProps) {
    return (
        <div
            className={clsx(
                "w-full max-w-full  sm:max-w-md md:max-w-lg lg:max-w-xl",
                "flex flex-col justify-start items-center",
                "border border-gray-200 dark:border-gray-700",
                "rounded-2xl shadow-md dark:bg-gray-900 bg-white ",
                "p-4 sm:p-6 md:p-8",
                className,
                cardStyles[varient]
            )}
        >
            {children}
        </div>
    );
}
