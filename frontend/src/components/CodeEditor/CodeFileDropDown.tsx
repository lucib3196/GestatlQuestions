import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import type { SelectChangeEvent } from "@mui/material/Select";



type CodeFileDropDownProps = {
    fileNames: string[];
    selectedFile: string;
    setSelectedFile: (val: string) => void;
};


function CodeFileDropDown({
    fileNames,
    selectedFile,
    setSelectedFile,
}: CodeFileDropDownProps) {
    const handleFileChange = (event: SelectChangeEvent) => {
        setSelectedFile(event.target.value as string);
    };

    return (
        <FormControl fullWidth size="small" sx={{ mt: 2 }}>
            <InputLabel id="code-file-select-label">File</InputLabel>
            <Select
                labelId="code-file-select-label"
                id="code-file-select"
                value={selectedFile}
                label="File"
                onChange={handleFileChange}
                sx={{ backgroundColor: "background.paper" }}
            >
                {fileNames.map((val) => (
                    <MenuItem key={val} value={val}>
                        {val}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>
    );
}

export default CodeFileDropDown