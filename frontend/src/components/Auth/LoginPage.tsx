import { signInWithEmailAndPassword } from "firebase/auth";
import AuthBase from "./AuthBase";
import { toast } from "react-toastify";
import { auth } from "../../config/firebaseClient";
import VerifyAccount from "./VerifyAccount";
import { useAuth } from "../../context/AuthContext";
import LogInSuccess from "./LogInSuccess";
import { useState } from "react";
import { sendPasswordResetEmail } from "firebase/auth";


export function LogInPage() {
  const { user } = useAuth();
  const [forgotPassword, setForgotPassword] = useState(false);
  const [email, setEmail] = useState("");

  const handleResetPassword = async () => {
    try {
      await sendPasswordResetEmail(auth, email);
      toast.info(`Password reset email sent to ${email}`);
      setForgotPassword(false);
    } catch (error: any) {
      toast.error(`Could not send password reset: ${error.message}`);
    }
  };

  const handleSubmit = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
      toast.success("Log In Successful");
    } catch (error) {
      toast.error(`Could not Log In ${error as string}`)
    }

  };

  // Handle user states
  if (user && !user?.emailVerified) {
    return <VerifyAccount />;
  }

  if (user && user.emailVerified) {
    return <LogInSuccess />;
  }

  // Forgot password form
  if (forgotPassword) {
    return (
      <div className="flex flex-col items-center justify-center space-y-4 p-8">
        <h2 className="text-xl font-semibold text-black">Reset Password</h2>
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-gray-300 rounded-md px-4 py-2 w-72 focus:ring-2 focus:ring-indigo-400 focus:outline-none text-black"
        />
        <button
          onClick={handleResetPassword}
          className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-md transition"
        >
          Send Reset Email
        </button>
        <button
          onClick={() => setForgotPassword(false)}
          className="text-indigo-400 hover:text-indigo-300 text-sm"
        >
          Back to Login
        </button>
      </div>
    );
  }

  // Default login form
  return (
    <div className="flex flex-col items-center justify-center">
      <AuthBase
        state="login"
        onSubmit={handleSubmit}
      >
        <a
          href="#"
          className="font-semibold text-indigo-400 hover:text-indigo-300 text-sm"
          onClick={() => setForgotPassword(true)}
        >
          Forgot password?
        </a>
      </AuthBase>
    </div>
  );
}