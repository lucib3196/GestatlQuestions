import AuthBase from "./AuthBase";
import { toast } from "react-toastify";

export function LogInPage() {
  const handleSubmit = (name: string, email: string, password: string) => {
    console.log("Submitted", name, email, password);
    toast.info(`Log In Success welcome ${name}`);
  };
  return (
    <div className="flex flex-col items-center justify-center">
      <AuthBase state="login" onSubmit={handleSubmit} />{" "}
    </div>
  );
}
