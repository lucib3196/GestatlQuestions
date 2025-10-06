import type React from "react"
import clsx from "clsx";

type PanelTheme = "boxshadow" | "primary"
const PanelStyles: Record<PanelTheme, string> = {
    boxshadow: "",
    primary: "",

};

type PanelProps = {
    children: React.ReactNode
    theme?: PanelTheme
    className?: string,
}


export default function Panel({ children, theme = "primary", className = "" }: PanelProps) {
    return (
        <div className={clsx("max-w-5xl mx-auto my-8 px-4 bg-white text-primary-blue dark:text-text-primary dark:bg-background overflow-auto", PanelStyles[theme],className)}>{children}</div>
    )
}