import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Eye, EyeOff, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface AdminLoginPageProps {
  onLogin: () => void;
}

const AdminLoginPage = ({ onLogin }: AdminLoginPageProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    // Simulate admin login check (mock validation)
    await new Promise((resolve) => setTimeout(resolve, 800));
    
    // Mock admin credentials check
    if (email === "admin@ocrbench.com" && password === "admin123") {
      setIsLoading(false);
      onLogin();
    } else {
      setIsLoading(false);
      setError("Invalid admin credentials");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-sm animate-scale-in">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="p-2 rounded-xl bg-destructive/10 border border-destructive/20">
            <Shield className="w-6 h-6 text-destructive" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">Admin Portal</h1>
        </div>

        {/* Card */}
        <div className="glass-card rounded-xl p-6">
          <div className="mb-6">
            <h2 className="text-lg font-medium mb-1">Admin Access</h2>
            <p className="text-sm text-muted-foreground">
              Sign in with admin credentials
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Admin Email</label>
              <Input
                type="email"
                placeholder="admin@ocrbench.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Password</label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              ) : (
                "Sign in as Admin"
              )}
            </Button>
          </form>

          <div className="mt-4 pt-4 border-t border-border">
            <button
              onClick={() => navigate("/")}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors w-full text-center"
            >
              ← Back to user login
            </button>
          </div>

          <p className="text-xs text-muted-foreground text-center mt-4">
            Demo Login: admin@ocrbench.com / admin123
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;
