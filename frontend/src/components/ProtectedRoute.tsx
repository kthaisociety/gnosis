import { Navigate, Outlet } from "react-router-dom";
import { authClient } from "@/lib/auth";

export default function ProtectedRoute() {
  const session = authClient.useSession();

  if (session.isPending) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  if (!session.data?.user) {
    return <Navigate to="/auth/sign-in" replace />;
  }

  return <Outlet />;
}
