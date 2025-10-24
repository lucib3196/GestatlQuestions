import React from "react";
import { MyModal } from "../Base/MyModal";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { LogInPage } from "./LoginPage";
import { SignUpPage } from "./SignUpPage";
import SectionContainer from "../Base/SectionContainer";
import { TitleHeader } from "./../Base/TitleHeader";
import { useAuth } from "../../context/AuthContext";
import { MyButton } from "../Base/Button";

type State = "login" | "signup";

type UserLoginProps = {
  show: boolean;
  setShow: () => void;
};

export default function UserLoginPage({ show, setShow }: UserLoginProps) {
  const [state, setState] = React.useState<State>("login");
  const { user, logout } = useAuth()

  const handleAlignment = (_: React.MouseEvent<HTMLElement>, state: State) => {
    setState(state);
  };

  return (
    <SectionContainer id="userLogin">
      {show && (
        <MyModal setShowModal={setShow} className="min-w-1/2 min-h-3/4 flex flex-col items-center justify-center">
          {/* Toggle For Login */}
          {/* Auth Toggle */}
          {!user && (
            <ToggleButtonGroup
              value={state}
              exclusive
              onChange={handleAlignment}
              aria-label="auth toggle"
              className="flex justify-center space-x-3"
            >
              <ToggleButton value="login" aria-label="login">
                Log In
              </ToggleButton>
              <ToggleButton value="signup" aria-label="signup">
                Sign Up
              </ToggleButton>
            </ToggleButtonGroup>
          )}

          {/* Logout */}
          {user && (
            <MyButton name="Log Out" onClick={logout} className="mt-4" />
          )}

          {/* Auth Forms */}
          <div className="w-full text-center">
            <TitleHeader value={state === "login" ? "Log In" : "Sign Up"} />
            {state === "login" ? <LogInPage /> : <SignUpPage />}
          </div>
        </MyModal>
      )}
    </SectionContainer>
  );
}
