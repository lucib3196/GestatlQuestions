import { onAuthStateChanged } from "firebase/auth";
import type { User } from "firebase/auth";
import { auth } from "../config/firebaseClient";
import { useState, useEffect } from "react";
import { createContext, useContext } from "react";




export function useStateAuth() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const unSubscribe = onAuthStateChanged(auth, (fbUser) => {
            if (fbUser) {
                console.log("User Signed In", fbUser.uid);
                setLoading(false);
                setUser(fbUser);
            } else {
                console.log("No User Logged in");
            }
        });
        return () => unSubscribe();
    }, []);

    return { user, loading };
}

type AuthContextType = {
    user: User | null;
    loading: boolean;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const { user, loading } = useStateAuth();

    const logout = async () => {
        await auth.signOut();
        window.location.reload();
    };
    return (
        <AuthContext.Provider value={{ user, loading, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
