import type { SxProps } from "@mui/material";
import type { Theme } from "../types/settingsType";
import { useMemo } from "react";


export const useToggleButtonSx = (mode?: Theme): SxProps => {
  
  return useMemo(() => ({
    padding: "0.5rem",
    transition: "all 0.2s ease-in-out",

    "&.Mui-selected": {
      backgroundColor:
        mode === "dark"
          ? "var(--color-accent-sky)"
          : "var(--color-white)",
      color:
        mode === "dark"
          ? "var(--text-primary)"
          : "var(--primary-blue)"
    },

    "&.Mui-selected:hover": {
      backgroundColor:
        mode === "dark"
          ? "var(--color-primary-blue)"
          : "var(--color-white)",
    },

    "&.Mui-selected.Mui-disabled": {
      backgroundColor: "var(--color-white)",
      opacity: 0.7,
    },

    "&:hover": {
      backgroundColor:
        mode === "dark"
          ? "var(--color-primary-blue)"
          : "var(--color-text-secondary)",
      color: "var(--color-primary-blue)",
    },
  }), [mode]);
};