import AuthBase from "./AuthBase"


export function SignUpPage() {
    const handleSubmit = (name: string, email: string, password: string) => {
        console.log("Submitted", name, email, password)
    }
    return (
        <div className="flex flex-col items-center justify-center">
            <h1>Sign Up</h1>
            <AuthBase state="signup" onSubmit={handleSubmit} />
        </div>
    )
}