import GenericForm from "./Generic";
import { MenuItem, Select, type SelectChangeEvent } from "@mui/material";

type AdaptiveDropDownProps = {
    adaptiveValue: boolean;
    setIsAdaptive: (val: boolean) => void;
    disabled?: boolean;
};

const AdaptiveDropDown = ({
    adaptiveValue,
    setIsAdaptive,
    disabled,
}: AdaptiveDropDownProps) => {
    const name = "Is Adaptive";
    const id = name.toLowerCase().replace(/\s+/g, "-");
    return (
        <GenericForm name={name}>
            <Select
                labelId={`${id}-label`}
                value={adaptiveValue ? "true" : "false"}
                onChange={(e: SelectChangeEvent) =>
                    setIsAdaptive((e.target.value.toLowerCase() as string) === "true")
                }
                label={name}
                disabled={disabled}
            >
                <MenuItem value="false">False</MenuItem>
                <MenuItem value="true">True</MenuItem>
            </Select>
        </GenericForm>
    );
};

export default AdaptiveDropDown