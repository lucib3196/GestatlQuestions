import type { CodeLanguage } from "../../types/settingsType";
import type { Dispatch, SetStateAction } from "react";
import { IoLogoJavascript } from "react-icons/io5";
import { FaPython } from "react-icons/fa";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { useState } from "react";
import { CiCircleInfo } from "react-icons/ci";
import { useToggleButtonSx } from "../../styles/ToggleButtonStyles";
import { useTheme } from "../Generic/DarkModeToggle";
type CodeSettingsProps = {
    language: CodeLanguage;
    setLanguage: Dispatch<SetStateAction<CodeLanguage>>;
};

export const CodeSettings = ({ language, setLanguage }: CodeSettingsProps) => {
    const [showHelp, setShowHelp] = useState<boolean>(false);
    const [theme] = useTheme();

    const sx = useToggleButtonSx(theme);
    const iconSize = "30px";


    const handleChange = (
        _: React.MouseEvent<HTMLElement>,
        newLanguage: CodeLanguage | null
    ) => {
        if (newLanguage) {
            setLanguage(newLanguage);
        }
    };

    return (
        <div className="flex flex-col items-center gap-y-3">
            {/* Title + Info */}
            <div className="flex flex-row items-center gap-x-2">
                <p className="font-semibold ">
                    Set Language
                </p>

                <div className="relative">
                    <CiCircleInfo
                        className="cursor-pointer text-gray-600 hover:text-accent-sky dark:text-gray-300 dark:hover:text-accent-teal transition-colors duration-200"
                        size={24}
                        onMouseEnter={() => setShowHelp(true)}
                        onMouseLeave={() => setShowHelp(false)}
                    />
                    {showHelp && (
                        <div
                            className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-64 p-3 text-sm rounded-lg shadow-lg z-50
                        bg-gray-800 text-white dark:bg-gray-900 dark:text-gray-100"
                        >
                            Choose how code should run when working with adaptive questions.
                        </div>
                    )}
                </div>
            </div>

            {/* Language Toggle */}
            <ToggleButtonGroup
                value={language}
                exclusive
                onChange={handleChange}
                className="rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600"
            >
                <ToggleButton
                    value="javascript"
                    aria-label="javascript"
                    sx={sx}
                    className="px-4 py-2 transition-colors duration-200 bg-gray-100 hover:bg-accent-sky/20 dark:bg-surface dark:hover:bg-accent-teal/20"
                >
                    <IoLogoJavascript size={iconSize} className="text-yellow-500" />
                </ToggleButton>

                <ToggleButton
                    value="python"
                    aria-label="python"
                    sx={sx}
                    className="px-4 py-2 transition-colors duration-200 bg-gray-100 hover:bg-accent-sky/20 dark:bg-surface dark:hover:bg-accent-teal/20"
                >
                    <FaPython size={iconSize} className="text-blue-500" />
                </ToggleButton>
            </ToggleButtonGroup>
        </div>
    );
};