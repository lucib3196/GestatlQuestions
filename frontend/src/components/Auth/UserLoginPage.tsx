import { MyModal } from "../Base/MyModal";
import { useState } from "react";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import React from "react";
import { LogInPage } from "./LoginPage";
import { SignUpPage } from "./SignUpPage";
import SectionContainer from "../Base/SectionContainer";

type State = "login" | "signup";

function Header({ value }: { value: string }) {
    return (
        <div className="flex flex-col items-center text-center space-y-1">
            <h1 className="text-xl font-semibold tracking-tight">{value}</h1>
            <div className="w-16 h-[2px] bg-gray-300 rounded" />
        </div>
    );
}
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
                            <Header value="LogIn"></Header>
                            <LogInPage />
                        </>
                    ) : (
                        <>
                            <Header value="SignUp"></Header>
                            <SignUpPage />
                        </>
                    )}
                </MyModal>
            )}
        </SectionContainer>
    );
}
