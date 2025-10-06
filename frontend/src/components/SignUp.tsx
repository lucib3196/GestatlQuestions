import { useState, type FormEvent } from "react";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import { signUpUser } from "../utils/firestoreAuth";

const roleOptions = ["admin", "professor", "developer"];
type Role = (typeof roleOptions)[number];

export default function SignUp() {
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState<Role>("developer");
    const [roleAuth, setRoleAuth] = useState("")
    const [error, setError] = useState("");
    console.log(error)
    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            signUpUser(email, password, role)
                ;
            console.log("User Signed Up: ");
        } catch (err: any) {
            setError(err.message);
        }
    };

    return (
        <form
            className="w-full max-w-lg border rounded-md p-6 bg-white"
            onSubmit={handleSubmit}
        >
            {/* First and Last Name Container */}
            <div className="flex flex-wrap -mx-3 mb-6">
                <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
                    <label
                        className="block uppercase tracking-wide text-gray-700 test-xs font-bold mb-2"
                        htmlFor="first-name"
                    >
                        First Name
                    </label>
                    <input
                        type="text"
                        className="appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white"
                        id="first-name"
                        placeholder="Richard"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        required
                    />
                </div>
                <div className="w-full md:w-1/2 px-3 mb-6 md:mb-0">
                    <label
                        className="block uppercase tracking-wide text-gray-700 test-xs font-bold mb-2"
                        htmlFor="last-name"
                    >
                        Last Name
                    </label>
                    <input
                        type="text"
                        className="appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white"
                        id="last-name"
                        placeholder="Feynman"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        required
                    />
                </div>
            </div>
            {/* Email */}
            <div className="flex flex-wrap -mx-3 mb-6">
                <div className="w-full px-3">
                    <label
                        className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2"
                        htmlFor="email"
                    >
                        Email
                    </label>
                    <input
                        className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
                        id="email"
                        type="email"
                        value={email}
                        placeholder="RFeynman@email.com"
                        onChange={(e) => setEmail(e.target.value)}
                    ></input>
                </div>
            </div>
            {/* PassWord */}
            <div className="flex flex-wrap -mx-3 mb-6">
                <div className="w-full px-3">
                    <label
                        className="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2"
                        htmlFor="password"
                    >
                        Password
                    </label>
                    <input
                        className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
                        id="password"
                        type="password"
                        placeholder="******************"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    ></input>
                </div>
            </div>

            {/* Roles and Authentication Token */}
            <div className="flex flex-wrap justify-center items-center -mx-3 mb-3">
                <div className="flex flex-col w-1/2 px-3">
                    <InputLabel id="role-select">Role</InputLabel>
                    <Select
                        labelId="role"
                        id="role"
                        value={role}
                        label="Role"
                        onChange={(e) => setRole(e.target.value)}
                    >
                        {roleOptions.map((r) => (
                            <MenuItem value={r}>{r.toUpperCase()}</MenuItem>
                        ))}
                    </Select>
                </div>
                <div className="flex flex-col w-1/2 px-3">
                    <InputLabel id="role-select">Role Auth Code</InputLabel>
                    <input
                        type="text"
                        className="appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white"
                        id="role-auth-code"
                        placeholder="**************"
                        value={roleAuth}
                        onChange={(e) => setRoleAuth(e.target.value)}
                        required
                    />
                </div>
            </div>

            {/* Submit Fields */}
            <div className=" flex flex-wrap justify-self-end-safe">
                <button
                    type="submit"
                    className="rounded-md px-3 py-2 text-white font-bold text-center bg-indigo-500 hover:bg-indigo-800"
                >
                    Sign Up
                </button>
            </div>
        </form>
    );
}
