import { createContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import api from "../api";


type LoggedInMessage = {
    username: string,
    success: string | boolean
}

export const AuthContext = createContext<{ isLoggedIn: boolean, message: LoggedInMessage | null }>({
    isLoggedIn: false,
    message: null
});

type AuthProviderProps = {
    children: ReactNode;
};



export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [loggedIn, setLoggedIn] = useState(false);
    const [message, setMessage] = useState<LoggedInMessage | null>(null)

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem("access_token");
            try {
                const response = await api.get("/auth/current_user", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                setMessage(response.data)
                setLoggedIn(true);
            } catch (err) {
                console.error("Auth check failed:", err);
                setLoggedIn(false);
            }
        };

        checkAuth();
    }, []);

    return (
        <AuthContext.Provider value={{ isLoggedIn: loggedIn, message }}>
            {children}
        </AuthContext.Provider>
    );
};
