import { useAuth } from "../../context/AuthContext";

export default function LogInSuccess() {
  const { user } = useAuth();
  return (
    <div className="text-gray-800 text-sm font-medium">
      ✅ Welcome, {user?.email || "User"}
    </div>
  );
}
