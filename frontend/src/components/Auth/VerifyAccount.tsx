import { sendEmailVerification } from "firebase/auth";
import { useAuth } from "../../context/AuthContext";
import { MyButton } from "../Base/Button";
import { useState } from "react";
import { toast } from "react-toastify";
import { useEffect } from "react";

export default function VerifyAccount() {
    const { user } = useAuth();
    const [coolDown, setCoolDown] = useState(false);
    const handleClick = async () => {
        if (!user) return;

        try {
            await sendEmailVerification(user);
            toast.info(`Sent verification to ${user.email}`);
            setCoolDown(true);
            setTimeout(() => setCoolDown(false), 50000);
        } catch (error: any) {
            toast.error(`Could not send verification email ${error.message}`);
        }
    };

    useEffect(() => {
        const interval = setInterval(async () => {
            if (user) {
                await user.reload();
                if (user.emailVerified) {
                    window.location.reload();
                }
            }
        }, 5000); // Every 5 seconds

        return () => clearInterval(interval);
    }, [user]);

    return (
        <div className="flex flex-col items-center text-gray-800 text-sm font-medium space-y-2">
            <p>Verify your email address to continue.</p>
            <MyButton
                name="Send Verification Email"
                disabled={coolDown}
                onClick={handleClick}
            />
        </div>
    );
}
