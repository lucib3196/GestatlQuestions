import type { QuestionStorage } from "../../types/settingsType";
import { GoFileDirectoryFill } from "react-icons/go";
import { FaCloud } from "react-icons/fa";
import { useState } from "react";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { CiCircleInfo } from "react-icons/ci";
import clsx from "clsx";
import { useToggleButtonSx } from "../../styles/ToggleButtonStyles";
import { useTheme } from "../Generic/DarkModeToggle";

type QuestionStorageProps = {
    questionStorageType: QuestionStorage
}
export const QuestionStorageSettings = ({ questionStorageType }: QuestionStorageProps) => {
    const [showHelp, setShowHelp] = useState<boolean>(false);
    const iconSize = "15px";
    const theme = useTheme()

    return (
        <div className="flex-1 flex flex-col items-center gap-y-2">
            {/* Header + Info Tooltip */}
            <div className="flex flex-row items-center gap-x-2">
                <p className="font-bold">Question Storage Settings</p>
                <div className="relative">
                    <CiCircleInfo
                        className="cursor-pointer text-gray-600"
                        size={24}
                        onMouseEnter={() => setShowHelp(true)}
                        onMouseLeave={() => setShowHelp(false)}
                    />
                    {showHelp && (
                        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-64 p-2 text-sm text-white bg-gray-800 rounded shadow-lg z-50">
                            Choose where questions are stored:
                            <br />• <b>Cloud</b>: Saves questions in online storage
                            <br />• <b>Local</b>: Saves questions on your device
                        </div>
                    )}
                </div>
            </div>

            {/* Toggle Buttons */}
            <ToggleButtonGroup
                value={questionStorageType}
                className="flex w-full items-center justify-center"
                exclusive
            >
                <ToggleButton
                    value="cloud"
                    disabled={questionStorageType !== "cloud"}
                    aria-label="cloud"
                    sx={useToggleButtonSx(theme)}
                >
                    <div
                        className={clsx(
                            "flex flex-col  items-center",
                            questionStorageType !== "cloud" && "cursor-not-allowed"
                        )}
                    >
                        <FaCloud size={iconSize} />
                        <p className="font-bold my-2">Cloud</p>
                    </div>
                </ToggleButton>

                <ToggleButton
                    value="local"
                    disabled={questionStorageType !== "local"}
                    aria-label="local"
                    sx={useToggleButtonSx(theme)}
                >
                    <div
                        className={clsx(
                            "flex flex-col  items-center",
                            questionStorageType !== "local" && "cursor-not-allowed"
                        )}
                    >
                        <GoFileDirectoryFill size={iconSize} />
                        <p className="font-bold my-2">Local</p>
                    </div>
                </ToggleButton>
            </ToggleButtonGroup>
        </div>
    );
};