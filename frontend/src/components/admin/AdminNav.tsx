import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Scan, Shield, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

interface AdminNavProps {
  onLogout: () => void;
}

const AdminNav = ({ onLogout }: AdminNavProps) => {
  const location = useLocation();
  
  const navItems = [
    { path: "/admin", label: "Admin Panel", icon: Shield },
    { path: "/admin/benchmark", label: "OCR Bench", icon: Scan },
  ];

  return (
    <header className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <nav className="flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-primary/10 text-primary border border-primary/20" 
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                )}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Button variant="ghost" size="sm" onClick={onLogout} className="gap-2">
          <LogOut className="w-4 h-4" />
          Sign out
        </Button>
      </div>
    </header>
  );
};

export default AdminNav;
