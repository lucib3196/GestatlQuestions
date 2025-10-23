import AuthBase from "./AuthBase";



export function LogInPage() {
    const handleSubmit = (name: string, email: string, password: string) => {
        console.log("Submitted", name, email, password)
    }
    return (
        <div>
            <h1>Log In</h1>
            <AuthBase state="login" onSubmit={handleSubmit} />
        </div>
    )
}

