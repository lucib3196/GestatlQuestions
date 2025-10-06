import type { SxProps } from "@mui/material";
import type { Theme } from "react-toastify";

export const tableHeaderSx = (mode: Theme): SxProps => {
  return {
    fontWeight: 600,
    fontSize: "0.95rem",
    transition: "all 0.2s ease-in-out",

    backgroundColor:
      mode === "dark"
        ? "var(--color-background)" // your dark header color
        : "var(--color-white)", // your light header color

    color: mode === "dark" ? "white" : "",

    "&:first-of-type": {
      borderTopLeftRadius: "0.5rem",
    },
    "&:last-of-type": {
      borderTopRightRadius: "0.5rem",
    },
  };
};
