import { toast } from "react-toastify";
import { IoIosAddCircle } from "react-icons/io";
import { FaMinusCircle } from "react-icons/fa";
import React from "react";

type Props = {
    value: number;
    onChange: (next: number) => void;
    max?: number;
    min?: number;
    className?: string;
};

export const AddQuestionInput: React.FC<Props> = ({
    value,
    onChange,
    max = 6,
    min = 1,
    className = "",
}) => {
    const canDec = value > min;
    const canInc = value < max;

    const inc = () => {
        if (!canInc) {
            toast.info(`Can only accept up to ${max} questions at a time`);
            return;
        }
        onChange(value + 1);
    };

    const dec = () => {
        if (!canDec) {
            toast.info(`Minimum is ${min} question${min === 1 ? "" : "s"}`);
            return;
        }
        onChange(value - 1);
    };

    return (
        <div
            className={[
                "inline-flex items-center gap-3 rounded-xl border border-gray-200",
                "bg-white/80 px-3 py-2 shadow-sm ring-1 ring-black/5",
                className,
            ].join(" ")}
        >
            <button
                type="button"
                onClick={dec}
                aria-label="Remove question"
                title={canDec ? "Remove question" : `Min ${min}`}
                disabled={!canDec}
                className={[
                    "inline-flex h-9 w-9 items-center justify-center rounded-full",
                    "border border-gray-200 bg-white text-gray-700 shadow-sm",
                    "transition hover:bg-indigo-50 hover:text-indigo-700",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500",
                    "disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-white",
                ].join(" ")}
            >
                <FaMinusCircle className="h-6 w-6" />
            </button>

            <span className="select-none rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700 tabular-nums">
                {value}
            </span>

            <button
                type="button"
                onClick={inc}
                aria-label="Add question"
                title={canInc ? "Add question" : `Max ${max} reached`}
                disabled={!canInc}
                className={[
                    "inline-flex h-9 w-9 items-center justify-center rounded-full",
                    "border border-gray-200 bg-white text-gray-700 shadow-sm",
                    "transition hover:bg-indigo-50 hover:text-indigo-700",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500",
                    "disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-white",
                ].join(" ")}
            >
                <IoIosAddCircle className="h-6 w-6" />
            </button>
        </div>
    );
};
