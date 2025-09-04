import { FormControl } from "@mui/material";
import { InputLabel } from "@mui/material";

type GenericFormProps = {
    name: string;
    children: React.ReactNode;
};

const GenericForm = ({ name, children }: GenericFormProps) => {
    return (
        <FormControl className="flex-[1_1_10rem] min-w-48 max-w-xl">
            <InputLabel id={`${name.toLowerCase().replace(/\s+/g, "-")}-label`}>
                <span className="text-base font-medium text-indigo-900">
                    {name.toUpperCase()}
                </span>
            </InputLabel>

            {children}
        </FormControl>
    );
};

export default GenericForm;