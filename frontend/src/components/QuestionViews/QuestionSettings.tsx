import { useState, useContext } from "react";
import { IoIosSettings } from "react-icons/io";
import { IoClose } from "react-icons/io5";
import { CiCircleInfo } from "react-icons/ci";
import {
    Modal,
    Box,
    Typography,
    IconButton,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
} from "@mui/material";

import { QuestionSettingsContext } from "../../context/GeneralSettingsContext";

const modalStyle = {
    position: "absolute" as const,
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 600,
    bgcolor: "background.paper",
    borderRadius: 2,
    boxShadow: 24,
    p: 4,
};

export default function QuestionSettings() {
    const [showSettings, setShowSettings] = useState<boolean>(false);
    const [showRenderingInfo, setShowRenderingInfo] = useState<boolean>(false);
    const [showCodeRunningInfo, setShowCodeRunningInfo] = useState<boolean>(false);
    const {
        renderingSettings,
        setRenderingSettings,
        codeRunningSettings,
        setCodeRunningSettings,
    } = useContext(QuestionSettingsContext);

    return (
        <div>
            {/* Settings Icon */}
            <IconButton onClick={() => setShowSettings(true)}>
                <IoIosSettings size={28} />
            </IconButton>

            {/* Settings Modal */}
            <Modal open={showSettings} onClose={() => setShowSettings(false)}>
                <Box sx={modalStyle}>
                    {/* Close Button */}
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="font-bold "> Settings</h2>


                        <IconButton onClick={() => setShowSettings(false)} size="small">
                            <IoClose size={24} />
                        </IconButton>
                    </div>

                    {/* Form Fields */}
                    <div className="flex items-center gap-4">
                        <FormControl fullWidth>
                            <InputLabel id="renderingSettings-label">
                                Question Rendering
                            </InputLabel>
                            <Select
                                labelId="renderingSettings-label"
                                id="renderingSettings"
                                value={renderingSettings}
                                label="Question Rendering"
                                onChange={(event) =>
                                    setRenderingSettings(event.target.value as "legacy" | "new")
                                }
                            >
                                <MenuItem value="new">New</MenuItem>
                                <MenuItem value="legacy">Legacy</MenuItem>
                            </Select>
                        </FormControl>

                        {/* Info Icon with Hover Box */}
                        <div className="relative">
                            <CiCircleInfo
                                className="cursor-pointer text-gray-600"
                                size={24}
                                onMouseEnter={() => setShowRenderingInfo(true)}
                                onMouseLeave={() => setShowRenderingInfo(false)}
                            />
                            {showRenderingInfo && (
                                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-64 p-2 text-sm text-white bg-gray-800 rounded shadow-lg z-50">
                                    <strong>New:</strong> uses the latest UI engine for rendering.
                                    <br />
                                    <strong>Legacy:</strong> uses the original PrairieLearn-style
                                    rendering.
                                </div>
                            )}
                        </div>

                        <FormControl fullWidth>
                            <InputLabel id="codeRunning-label">Code Language </InputLabel>
                            <Select
                                labelId="codeRunning-label"
                                id="codeRunningSettings"
                                value={codeRunningSettings}
                                label="Code Language"
                                onChange={(event) =>
                                    setCodeRunningSettings(
                                        event.target.value as "javascript" | "python"
                                    )
                                }
                            >
                                <MenuItem value="javascript">JavaScript</MenuItem>
                                <MenuItem value="python">Python</MenuItem>
                            </Select>
                        </FormControl>
                        <div className="relative">
                            <CiCircleInfo
                                className="cursor-pointer text-gray-600"
                                size={24}
                                onMouseEnter={() => setShowCodeRunningInfo(true)}
                                onMouseLeave={() => setShowCodeRunningInfo(false)}
                            />
                            {showCodeRunningInfo && (
                                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-64 p-2 text-sm text-white bg-gray-800 rounded shadow-lg z-50">
                                    <strong>Javascript:</strong> Uses Javascript for generating values
                                    <br />
                                    <strong>Python:</strong> uses Python for generating values
                                </div>
                            )}
                        </div>
                    </div>

                </Box>
            </Modal>
        </div>
    );
}
