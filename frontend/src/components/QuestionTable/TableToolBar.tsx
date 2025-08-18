// src/features/questions/TableToolbar.tsx
import React from "react";
import { MdDelete } from "react-icons/md";

type Props = {
    canAct: boolean;
    count: number;
    onDelete: () => void;
    onRunTests: () => void;
    onHandleDownload: () => void
};

export function TableToolbar({ canAct, count, onDelete, onRunTests, onHandleDownload }: Props) {
    return (
        <div className="w-full border flex items-center justify-center mb-10 py-3 gap-3">


            <button
                type="button"
                onClick={onRunTests}
                disabled={!canAct}
                className={[
                    "border-2 px-3 py-1 rounded-md transition",
                    canAct
                        ? "border-blue-600 text-blue-700 hover:bg-blue-200"
                        : "border-gray-300 text-gray-400 cursor-not-allowed",
                ].join(" ")}
            >
                Run Tests
            </button>
            <button type="button"
                onClick={onHandleDownload} className={[
                    "border-2 px-3 py-1 rounded-md transition",
                    canAct
                        ? "border-green-600 text-green-700 hover:bg-green-200"
                        : "border-gray-300 text-gray-400 cursor-not-allowed",
                ].join(" ")}>
                Download Questions
            </button>
            <button
                type="button"
                onClick={canAct ? onDelete : undefined}
                disabled={!canAct}
                title={canAct ? `Delete ${count} selected` : "Select questions to enable delete"}
                aria-label="Delete selected questions"
                className={[
                    "inline-flex items-center rounded-md p-2 transition",
                    canAct
                        ? "text-red-600 hover:text-red-700 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                        : "text-gray-400 cursor-not-allowed",
                ].join(" ")}
            >
                <div className="flex flex-row justify-baseline">
                    Delete Questions <MdDelete size={20} />

                </div>

                <span className="sr-only">Delete</span>
            </button>
        </div>
    );
}