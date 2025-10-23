import React, { useState } from "react";
import { MyModal } from "../Base/MyModal";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { LogInPage } from "./LoginPage";
import { SignUpPage } from "./SignUpPage";
import SectionContainer from "../Base/SectionContainer";

import { TitleHeader } from './../Base/TitleHeader';



type State = "login" | "signup";


export default function UserLoginPage() {
    const [showModal, setShowModal] = useState<boolean>(true);
    const [state, setState] = React.useState<State>("login");

    const handleAlignment = (_: React.MouseEvent<HTMLElement>, state: State) => {
        setState(state);
    };

    return (
        <SectionContainer id="userLogin">
            {showModal && (
                <MyModal setShowModal={setShowModal} className="min-w-1/2 min-h-1/2">
                    {/* Toggle For Login */}
                    <div>
                        <ToggleButtonGroup
                            value={state}
                            exclusive
                            onChange={handleAlignment}
                            aria-label="text alignment"
                        >
                            <ToggleButton value="login" aria-label="left aligned">
                                LogIn
                            </ToggleButton>
                            <ToggleButton value="signup" aria-label="left aligned">
                                Sign Up
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </div>
                    {state === "login" ? (
                        <>
                            <TitleHeader value="LogIn"></TitleHeader>
                            <LogInPage />
                        </>
                    ) : (
                        <>
                            <TitleHeader value="SignUp"></TitleHeader>
                            <SignUpPage />
                        </>
                    )}
                </MyModal>
            )}
        </SectionContainer>
    );
}
