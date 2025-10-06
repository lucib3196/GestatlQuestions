import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { IoLockClosedOutline } from "react-icons/io5";
import { IoLockOpenOutline } from "react-icons/io5";
import { useTheme } from "../Generic/DarkModeToggle";
import { useToggleButtonSx } from "../../styles/ToggleButtonStyles";
import { genericIconColor } from './../../styles/IconStyles';
import type { ViewMode } from "../../types/settingsType";

type MinimalToggleProps = {
    viewMode: ViewMode,
    onChange: (mode: ViewMode) => void
}
export function MinimalToggle({ viewMode, onChange }: MinimalToggleProps) {
    const [theme] = useTheme(); 
    const sx = useToggleButtonSx(theme); 

    const handleViewChange = (
        _event: React.MouseEvent<HTMLElement>,
        newValue: ViewMode | null
    ) => {
        if (newValue !== null) {
            onChange(newValue);
        }
    };

    return (
        <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewChange}
            className="rounded-lg border border-gray-300 dark:border-gray-600"
        >
            <ToggleButton value="minimal" className="flex gap-2 items-center" sx={sx}>
                <IoLockClosedOutline color={genericIconColor(theme)} />
            </ToggleButton>

            <ToggleButton value="full" className="flex gap-2 items-center" sx={sx}>
                <IoLockOpenOutline color={genericIconColor(theme)} />
            </ToggleButton>
        </ToggleButtonGroup>
    );
}