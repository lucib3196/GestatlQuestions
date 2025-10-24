import { useAuth } from "../../context/AuthContext";
import { MyButton } from "../Base/Button";
import { deleteUser } from "firebase/auth";
import { toast } from "react-toastify";


export default function UserPage() {
    const { user, logout } = useAuth();

    const deleteAccount = async () => {
        if (!user) return;
        try {
            await deleteUser(user);
            toast.success("Account deleted successfully.");
            window.location.reload();
        } catch (error: any) {
            toast.error(`Could not delete account: ${error.message}`);
        }
    };

    if (!user) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <h2 className="text-xl font-semibold text-gray-700">Not logged in</h2>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-6">
            <div className="bg-white shadow-md rounded-lg p-8 w-full max-w-md text-center space-y-6 border border-gray-200">
                <h1 className="text-2xl font-bold text-gray-800">
                    Welcome, {user.email}
                </h1>
                <p className="text-gray-600">You are currently logged in.</p>

                <div className="flex flex-col space-y-3">
                    <MyButton name="Logout" onClick={logout} />
                    <MyButton
                        name="Delete Account"
                        onClick={deleteAccount}
                        className="bg-red-500 hover:bg-red-600 text-white"
                    />
                </div>
            </div>
        </div>
    );
}
