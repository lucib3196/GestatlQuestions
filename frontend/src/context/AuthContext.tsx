import { createContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import api from "../api/api";


type LoggedInMessage = {
    username: string,
    email?: string,
    success: string | boolean
}

type SignUpProps = {
    username: string;
    fullname: string;
    email: string;
    disabled: boolean;
    password: string;
}

type LogInProps = {
    username: string,
    password: string
}

type AuthContextType = {
    isLoggedIn: boolean;
    message: LoggedInMessage | null;
    login: (message: LogInProps) => Promise<boolean>;
    logout: () => void;
    signUp: (message: SignUpProps) => Promise<boolean>;
};

export const AuthContext = createContext<AuthContextType>({
    isLoggedIn: false,
    message: null,
    login: async (_message: LogInProps) => false,
    logout: () => { },
    signUp: async (_message: SignUpProps) => true
});

type AuthProviderProps = {
    children: ReactNode;
};

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [isLoggedIn, setLoggedIn] = useState(false);
    const [message, setMessage] = useState<LoggedInMessage | null>(null)


    const login = async (message: LogInProps) => {
        try {
            const formData = new URLSearchParams();
            formData.append("username", message.username);
            formData.append("password", message.password);
            const response = await api.post("/auth/login", formData.toString(), {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            const data = response.data;
            console.log(data)
            console.log("This is the login data", data)
            localStorage.setItem("access_token", data.access_token);
            setMessage({ username: data.username, email: data.email, success: true });
            setLoggedIn(true)
            return true
        } catch (error) {
            console.error("Login error:", error);
            setLoggedIn(false)
            setMessage(null)
            setLoggedIn(false)
            return false
        }
    }

    const signUp = async (signUpMessage: SignUpProps) => {
        try {
            const formData = new FormData();

            formData.append("username", signUpMessage.username)
            formData.append("fullname", signUpMessage.fullname)
            formData.append("email", signUpMessage.email)
            formData.append("password", signUpMessage.password)
            formData.append("disabled", signUpMessage.disabled ? "true" : "false");
            const response = await api.post("/auth/signup", formData, {
                headers: {
                    "Content-Type": "application/json",
                },
            });
            const data = response.data;
            setMessage({ username: data.username, success: true });
            return true
        } catch (error) {
            console.error("Sign Up error:", error);
            setMessage(null)
            return false
        }

    }

    const logout = () => {
        localStorage.setItem("access_token", "");
        setLoggedIn(false);
        setMessage(null);
    }

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem("access_token");
            try {
                const response = await api.get("/auth/current_user", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                console.log("Checking Auth ", response)

                setMessage(response.data)
                setLoggedIn(true);
            } catch (err) {
                console.error("Auth check failed:", err);
                setLoggedIn(false);
            }
        };

        checkAuth();
    }, [isLoggedIn]);

    return (
        <AuthContext.Provider value={{ isLoggedIn, message, login, logout, signUp }}>
            {children}
        </AuthContext.Provider>
    );
};
