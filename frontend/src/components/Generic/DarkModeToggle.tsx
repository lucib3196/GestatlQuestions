import { useEffect, useState } from "react";
import { MdLightMode, MdDarkMode } from "react-icons/md";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useToggleButtonSx } from "../../styles/ToggleButtonStyles";
import { genericIconColor } from "../../styles/IconStyles";

type Theme = "light" | "dark";

// --- Utility: read from localStorage ---
function getStoredTheme(): Theme {
    const stored = localStorage.getItem("theme");
    return stored === "dark" ? "dark" : "light";
}

// --- Hook: manages theme state + syncs everywhere ---
export function useTheme() {
    const [theme, setTheme] = useState<Theme>(getStoredTheme);

    // Apply theme to <html> + persist in localStorage
    useEffect(() => {
        document.documentElement.classList.toggle("dark", theme === "dark");
        localStorage.setItem("theme", theme);
    }, [theme]);

    // Listen for localStorage changes (multi-tab sync)
    useEffect(() => {
        const handler = () => setTheme(getStoredTheme());
        window.addEventListener("storage", handler);
        return () => window.removeEventListener("storage", handler);
    }, []);

    return [theme, setTheme] as const;
}

// --- Toggle component ---
export function DarkModeToggle() {
    const [theme, setTheme] = useTheme();
    const iconColor = genericIconColor(theme); // <- keep your util

    const handleChange = (_: React.MouseEvent<HTMLElement>, mode: Theme | null) => {
        if (mode) setTheme(mode);
    };

    return (
        <div className="mx-10 my-auto flex items-center justify-end text-text-primary transition-colors duration-300">
            <ToggleButtonGroup
                className="rounded-full border border-surface dark:border-text-secondary"
                value={theme}
                exclusive
                onChange={handleChange}
            >
                <ToggleButton
                    className="rounded-full p-2"
                    value="light"
                    aria-label="Light mode"
                    sx={useToggleButtonSx(theme)}
                >
                    <MdLightMode color={iconColor} />
                </ToggleButton>
                <ToggleButton
                    className="rounded-full p-2"
                    value="dark"
                    aria-label="Dark mode"
                    sx={useToggleButtonSx(theme)}
                >
                    <MdDarkMode color={iconColor} />
                </ToggleButton>
            </ToggleButtonGroup>
        </div>
    );
}