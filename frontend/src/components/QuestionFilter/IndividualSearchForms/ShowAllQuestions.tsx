
import {
    Checkbox,
    FormControl,
} from "@mui/material";
import { FormControlLabel } from "@mui/material";



type showAllQuestionsProp = {
    checked: boolean;
    onChange: (arg: boolean) => void;
};
// All the Individiual Form Elements
export const ShowAllQuestionsCheckBox = ({ checked, onChange }: showAllQuestionsProp) => {
    return (
        <FormControl className="flex-[1_1_10rem] min-w-48 max-w-xl">
            <FormControlLabel
                control={
                    <Checkbox
                        checked={checked}
                        onChange={(_, check) => onChange(check)}
                    />
                }
                label={
                    <span className="text-base font-medium text-indigo-900">
                        Show All Questions
                    </span>
                }
            />
        </FormControl>
    );
};
