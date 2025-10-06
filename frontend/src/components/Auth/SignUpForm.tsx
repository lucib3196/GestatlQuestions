import React, { useContext, useState } from "react";
import { AuthContext } from "../../context/AuthContext";

type LogInFormProps = {
    setErrorMessage: (msg: string) => void;
    onSuccess: () => void
};

export default function SignUpForm({ setErrorMessage, onSuccess }: LogInFormProps) {
    const [username, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [firstName, setFirstName] = useState<string>("");
    const [lastName, setLastName] = useState<string>("")
    const [email, setEmail] = useState<string>("");
    const [disabled, _] = useState<boolean>(false);
    const { signUp } = useContext(AuthContext);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const fullname = firstName + " " + lastName
        const success = await signUp({ username, fullname, email, disabled, password });
        if (!success) {
            setErrorMessage("Sign-up failed. Please try again.");
        }
        else {
            onSuccess()
        }
    };


    return (
        <form
            className="flex flex-wrap gap-x-6 gap-y-8 items-start justify-center w-full h-full"
            onSubmit={handleSubmit}
        >
            {/* First Name */}
            <div className="w-[45%] min-w-[200px]">
                <label htmlFor="firstName" className="block text-sm font-medium text-black">
                    First Name
                </label>
                <input
                    id="firstName"
                    name="firstName"
                    type="text"
                    placeholder="Richard"
                    required
                    value={firstName}
                    onChange={(e) => {
                        setFirstName(e.target.value);
                        setErrorMessage("");
                    }}
                    className="mt-2 block w-full rounded-md bg-white/5 px-3 py-2 text-sm text-black placeholder:text-gray-500   outline-black focus:outline-2 focus:outline-indigo-500"
                />
            </div>

            {/* Last Name */}
            <div className="w-[45%] min-w-[200px]">
                <label htmlFor="lastName" className="block text-sm font-medium text-black">
                    Last Name
                </label>
                <input
                    id="lastName"
                    name="lastName"
                    type="text"
                    placeholder="Feynman"
                    required
                    value={lastName} // ✅ fixed: use `lastName`
                    onChange={(e) => {
                        setLastName(e.target.value);
                        setErrorMessage("");
                    }}
                    className="mt-2 block w-full rounded-md bg-white/5 px-3 py-2 text-sm text-black placeholder:text-gray-500  outline-1outline outline-black focus:outline-2 focus:outline-indigo-500"
                />
            </div>

            {/* Username */}
            <div className="w-[45%] min-w-[200px]">
                <label htmlFor="username" className="block text-sm font-medium text-black">
                    Username
                </label>
                <input
                    id="username"
                    name="username"
                    type="text"
                    placeholder="richardfeynman123"
                    required
                    value={username}
                    onChange={(e) => {
                        setUserName(e.target.value);
                        setErrorMessage("");
                    }}
                    className="mt-2 block w-full rounded-md bg-white/5 px-3 py-2 text-sm text-black placeholder:text-gray-500  outline-black focus:outline-2 focus:outline-indigo-500"
                />
            </div>

            {/* Email */}
            <div className="w-[45%] min-w-[200px]">
                <label htmlFor="email" className="block text-sm font-medium text-black">
                    Email
                </label>
                <input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="richard@caltech.edu"
                    required
                    value={email}
                    onChange={(e) => {
                        setEmail(e.target.value);
                        setErrorMessage("");
                    }}
                    className="mt-2 block w-full rounded-md bg-white/5 px-3 py-2 text-sm text-black placeholder:text-gray-500   outline-black focus:outline-2 focus:outline-indigo-500"
                />
            </div>

            {/* Password */}
            <div className="w-[93%] min-w-[200px]">
                <label htmlFor="password" className="block text-sm font-medium text-black">
                    Password
                </label>
                <input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="••••••••"
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => {
                        setPassword(e.target.value);
                        setErrorMessage("");
                    }}
                    className="mt-2 block w-full rounded-md bg-white/5 px-3 py-2 text-sm text-black placeholder:text-gray-500  outline-black focus:outline-2 focus:outline-indigo-500"
                />
            </div>

            {/* Submit Button */}
            <div className="w-[93%] min-w-[200px]">
                <button
                    type="submit"
                    className="mt-4 w-full justify-center rounded-md bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400 focus:outline-2 focus:outline-offset-2 focus:outline-indigo-500"
                >
                    Sign Up
                </button>
            </div>
        </form>
    );
}
