import React, { useContext, useState } from "react";
import { AuthContext } from "../../context/AuthContext";

type LogInFormProps = {
    setErrorMessage: (msg: string) => void;
};



export default function LogInForm({ setErrorMessage }: LogInFormProps) {
    const [username, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const { login } = useContext(AuthContext)

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const success = await login({ username, password });
        if (!success) {
            setErrorMessage("Incorrect username or password. Please try again.");
        }
    };
    return (
        <form
            className="flex grow w-full flex-col space-y-10 h-full"
            onSubmit={handleSubmit}
        >
            <div>
                <label
                    htmlFor="username"
                    className="block text-sm font-medium text-black"
                >
                    UserName
                </label>
                <div className="mt-2">
                    <input
                        id="username"
                        name="username"
                        type="text"
                        placeholder="User Name"
                        required
                        value={username}
                        onChange={(e) => {
                            setUserName(e.target.value);
                            setErrorMessage("")
                        }}
                        className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-black outline-1 outline-black placeholder:text-gray-500 focus:outline-2 focus:outline-indigo-500 sm:text-sm"
                    />
                </div>
            </div>

            <div>
                <div className="flex items-center justify-between">
                    <label
                        htmlFor="password"
                        className="block text-sm font-medium text-black"
                    >
                        Password
                    </label>
                    <div className="text-sm">
                        <a
                            href="#"
                            className="font-semibold text-indigo-400 hover:text-indigo-300"
                        >
                            Forgot password?
                        </a>
                    </div>
                </div>
                <div className="mt-2">
                    <input
                        id="password"
                        name="password"
                        type="password"
                        value={password}
                        onChange={(e) => {
                            setPassword(e.target.value);
                            setErrorMessage("")
                        }}
                        required
                        autoComplete="current-password"
                        className="block w-full rounded-md bg-white/50 px-3 py-1.5 text-base text-black outline-1 outline-black placeholder:text-gray-500 focus:outline-2 focus:outline-indigo-500 sm:text-sm"
                    />
                </div>
            </div>

            <div>
                <button
                    type="submit"
                    className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
                >
                    Sign in
                </button>
            </div>
        </form>
    );
}