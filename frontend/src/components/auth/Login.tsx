import React, { useContext, useState } from "react";
import api from "../../api";
import { AuthContext } from "../../context/AuthContext";

async function handleLogin(username: string, password: string): Promise<boolean> {
    try {
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await api.post("/auth/login", formData.toString(), {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        });

        const data = response.data;
        localStorage.setItem("access_token", data.access_token);
        return true;
    } catch (error) {
        console.error("Login error:", error);
        return false;
    }
}

function LogInForm() {

    const [username, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const success = await handleLogin(username, password)
        console.log(success);
    };
    return (
        <form
            className="flex grow w-full flex-col space-y-10 h-full"
            onSubmit={handleSubmit}
        >
            <div>
                <label htmlFor="username" className="block text-sm font-medium text-black">
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
                        onChange={(e) => setUserName(e.target.value)}
                        className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-black outline-1 outline-black placeholder:text-gray-500 focus:outline-2 focus:outline-indigo-500 sm:text-sm"
                    />
                </div>
            </div>

            <div>
                <div className="flex items-center justify-between">
                    <label htmlFor="password" className="block text-sm font-medium text-black">
                        Password
                    </label>
                    <div className="text-sm">
                        <a href="#" className="font-semibold text-indigo-400 hover:text-indigo-300">
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
                        onChange={(e) => setPassword(e.target.value)}
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


type LoggedInProps = {
    username: string;
};

function LoggedIn({ username }: LoggedInProps): React.ReactNode {
    return (
        <div className="self-start space-y-2">
            <p className="text-lg ">Thanks for logging in</p>
            <h1 className="font-bold text-2xl">Username: {username}</h1>
        </div>
    );
}


function LoginPage() {
    const { isLoggedIn, message } = useContext(AuthContext);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-opacity-50">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-1/2 min-w-2/5 min-h-1/2 max-h-3/4 flex flex-col justify-start px-6 py-12 lg:px-8">
                <div className="flex flex-col grow w-full h-full justify-evenly px-10">
                    {(isLoggedIn && message) ? <LoggedIn username={message.username}></LoggedIn> : <> <h2 className="mt-10 text-center text-2xl font-bold tracking-tight text-black">
                        Log in to Your Account
                    </h2>
                        <LogInForm /> </>}
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
