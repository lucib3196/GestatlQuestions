import { DarkModeToggle } from "./Generic/DarkModeToggle"

export function Header() {
    return (
        <header className="w-full h-20 flex items-end justify-end px-4 bg-bg-base dark:bg-background">
            <DarkModeToggle />
        </header>
    );
}
