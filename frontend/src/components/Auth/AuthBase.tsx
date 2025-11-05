
import { useState } from "react";
import type { FormEvent } from "react";
import { MyButton } from "../Base/Button";
import { InputTextForm } from './../Forms/InputComponents';


type State = "login" | "signup" | "resetPassword"


type AuthProps = {
    onSubmit: (email: string, password: string, username?: string) => Promise<void>;
    state: State;
    children?: React.ReactNode
};
export default function AuthBase({ state, onSubmit, children }: AuthProps) {
    const [_, setName] = useState<string>("");
    const [username, setUserName] = useState<string>("");
    const [email, setEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        console.log(email);
        onSubmit(email, password, username);
    };

    

    return (
        <form
            onSubmit={handleSubmit}
            className="flex flex-wrap flex-col  gap-y-3 items-center justify-center w-full h-full"
            id={state}
        >
            {state === "signup" && (
                <InputTextForm
                    id="name"
                    type="text"
                    name="name"
                    label="Name"
                    placeholder="Freddy"
                    onChange={(e) => setName(e.target.value)}
                />
            )}
            {state === "signup" && (
                <InputTextForm
                    id="username"
                    type="text"
                    name="username"
                    label="Username"
                    placeholder="FreeBodyFreddy"
                    onChange={(e) => setUserName(e.target.value)}
                />
            )}
            <InputTextForm
                id="email"
                type="email"
                name="email"
                label="Email"
                placeholder="FBody@email.com"
                onChange={(e) => setEmail(e.target.value)}
            />
            <InputTextForm
                id="password"
                type="password"
                name="password"
                label="Password"
                placeholder="*********"
                onChange={(e) => setPassword(e.target.value)}
            />
            {children}


            <MyButton btype="submit" name={state === "login" ? "Login" : "SignUp"} />
        </form>
    );
}
