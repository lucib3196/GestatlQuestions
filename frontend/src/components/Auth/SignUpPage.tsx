export function SignUpPage() {
    const handleSubmit = (name: string, email: string, password: string) => {
        console.log("Submitted", name, email, password)
    }
    return (
        <div>
            <h1>Sign Up</h1>
            <AuthBase state="signup" onSubmit={handleSubmit} />
        </div>
    )
}