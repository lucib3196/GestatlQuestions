import AuthBase from "./AuthBase";
import { toast } from "react-toastify";
import { FirebaseError } from "firebase/app";

import {
    createUserWithEmailAndPassword,
    sendEmailVerification,
} from "firebase/auth";
import { auth } from "../../config/firebaseClient";

export function SignUpPage() {
    const handleSubmit = async (
        email: string,
        password: string,
    ) => {
        try {
            const userCredential = await createUserWithEmailAndPassword(
                auth,
                email,
                password
            );
            const user = userCredential.user;

            if (user && !user.emailVerified) {
                await sendEmailVerification(user);
                toast.info(`A verification email has been sent to ${email}  `);
            }
        } catch (error) {
            let errorMsg = "";
            if (error instanceof FirebaseError) {
                errorMsg = error.message;
            }
            toast.error(`Could not create account ${errorMsg ?? ""}`);
        }
    };
    return (
        <div className="flex flex-col items-center justify-center">
            <AuthBase state="signup" onSubmit={handleSubmit} />
        </div>
    );
}
