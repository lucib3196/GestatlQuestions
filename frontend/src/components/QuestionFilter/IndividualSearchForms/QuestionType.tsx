import GenericForm from "./Generic";
import {
    MenuItem,
    Select,
    type SelectChangeEvent,
} from "@mui/material";

type QuestionTypeDropDownProps = {
    questionType: string;
    questionTypeOptions: string[];
    setQuestionType: (val: string) => void;
    disabled?: boolean;
};

const QuestionTypeDropDown = ({
    questionType,
    questionTypeOptions,
    setQuestionType,
    disabled,
}: QuestionTypeDropDownProps) => {
    const name = "Question Type";
    const id = name.toLowerCase().replace(/\s+/g, "-");

    return (
        <GenericForm name={name}>
            <Select
                labelId={`${id}-label`}
                value={questionType}
                onChange={(e: SelectChangeEvent) => setQuestionType(e.target.value as string)}
                label={name}
                disabled={disabled}
            >
                {questionTypeOptions.map((opt) => (
                    <MenuItem key={opt} value={opt}>
                        <span className="text-base font-medium text-indigo-900">{opt}</span>
                    </MenuItem>
                ))}
            </Select>
        </GenericForm>
    );
};

export default QuestionTypeDropDown;
