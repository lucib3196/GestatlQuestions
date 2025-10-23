import AuthBase from "./AuthBase"
import { toast } from "react-toastify"

export function SignUpPage() {
    const handleSubmit = (name: string, email: string, password: string) => {
        console.log("Submitted", name, email, password)
        toast.success(`Welcome to Gestalt ${name}`)

    }
    return (
        <div className="flex flex-col items-center justify-center">
            <AuthBase state="signup" onSubmit={handleSubmit} />
        </div>
    )
}