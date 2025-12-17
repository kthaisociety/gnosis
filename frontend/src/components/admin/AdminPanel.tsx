import { Shield, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import HealthCheck from "./HealthCheck";
import UserManagement from "./UserManagement";

interface AdminPanelProps {
  onLogout: () => void;
}

const AdminPanel = ({ onLogout }: AdminPanelProps) => {
  return (
    <div className="min-h-screen p-6 md:p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-destructive/10 border border-destructive/20">
              <Shield className="w-6 h-6 text-destructive" />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-tight">Admin Panel</h1>
              <p className="text-sm text-muted-foreground">Manage users and monitor system health</p>
            </div>
          </div>
          <Button variant="ghost" onClick={onLogout} className="gap-2">
            <LogOut className="w-4 h-4" />
            Sign out
          </Button>
        </div>

        {/* Health Check */}
        <HealthCheck />

        {/* User Management */}
        <UserManagement />
      </div>
    </div>
  );
};

export default AdminPanel;
