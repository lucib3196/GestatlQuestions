import type { Theme } from "../types/settingsType";

export function genericIconColor(theme:Theme){
    if (theme==="dark"){
        return "var(--color-white)"
    }else{
        return "var(--color-accent-sky)"
    }
}



