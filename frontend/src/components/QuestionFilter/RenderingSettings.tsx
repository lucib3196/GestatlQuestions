import type { RenderingType } from "../../types/settingsType";
import type { Dispatch, SetStateAction } from "react";
import { useState } from "react";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { CiCircleInfo } from "react-icons/ci";
import { useToggleButtonSx } from "../../styles/ToggleButtonStyles";
import { useTheme } from "../Generic/DarkModeToggle";


type RenderingSettingsProps = {
    renderingType: RenderingType,
    setRenderingType: Dispatch<SetStateAction<RenderingType>>
}


export const RenderingSettings = ({ renderingType, setRenderingType }: RenderingSettingsProps) => {
    const [showHelp, setShowHelp] = useState<boolean>(false);
    const handleChange = (
        _: React.MouseEvent<HTMLElement>,
        newLanguage: RenderingType | null
    ) => {
        if (newLanguage) {
            setRenderingType(newLanguage);
        }
    };
    const [theme] = useTheme();

    const sx = useToggleButtonSx(theme);

    return (
        <div className="flex flex-col items-center gap-y-2">
            <div className="flex flex-row items-center gap-x-2">
                <p className="font-bold ">Set Rendering Settings</p>
                <div className="relative">
                    <CiCircleInfo
                        className="cursor-pointer text-gray-600"
                        size={24}
                        onMouseEnter={() => setShowHelp(true)}
                        onMouseLeave={() => setShowHelp(false)}
                    />
                    {showHelp && (
                        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-64 p-2 text-sm text-white bg-gray-800 rounded shadow-lg z-50">
                            Choose how questions are displayed:
                            <br />• <b>Legacy</b>: Shows questions using HTML templates
                            <br />• <b>React</b>: Shows questions using React components
                        </div>
                    )}
                </div>
            </div>

            <ToggleButtonGroup value={renderingType} exclusive onChange={handleChange}>
                <ToggleButton value="legacy" aria-label="legacy" sx={sx}>
                    Legacy
                </ToggleButton>
                <ToggleButton disabled={true} className="hover:cursor-not-allowed" value="new" aria-label="new" sx={sx}>New</ToggleButton>
            </ToggleButtonGroup>
        </div>
    );
};
