import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Eye, EyeOff, UserPlus, CheckCircle, XCircle } from "lucide-react";
import { userStore } from "@/stores/userStore";
import { toast } from "sonner";

const InvitePage = () => {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidToken, setIsValidToken] = useState<boolean | null>(null);
  const [userEmail, setUserEmail] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!token) {
      setIsValidToken(false);
      return;
    }

    const user = userStore.getUserByInviteToken(token);
    if (user) {
      setIsValidToken(true);
      setUserEmail(user.email);
      setName(user.name);
    } else {
      setIsValidToken(false);
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setIsLoading(true);

    // Simulate activation
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const user = userStore.activateUser(token!, name);
    
    if (user) {
      setIsComplete(true);
      toast.success("Account activated successfully!");
    } else {
      toast.error("Failed to activate account");
    }

    setIsLoading(false);
  };

  if (isValidToken === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  if (!isValidToken) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-sm animate-scale-in text-center">
          <div className="glass-card rounded-xl p-8">
            <div className="p-3 rounded-full bg-destructive/10 border border-destructive/20 w-fit mx-auto mb-4">
              <XCircle className="w-8 h-8 text-destructive" />
            </div>
            <h2 className="text-lg font-medium mb-2">Invalid Invite Link</h2>
            <p className="text-sm text-muted-foreground mb-6">
              This invite link is invalid or has expired. Please contact your administrator for a new invite.
            </p>
            <Button onClick={() => navigate("/")} variant="outline">
              Go to Login
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-sm animate-scale-in text-center">
          <div className="glass-card rounded-xl p-8">
            <div className="p-3 rounded-full bg-emerald-500/10 border border-emerald-500/20 w-fit mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-emerald-500" />
            </div>
            <h2 className="text-lg font-medium mb-2">Account Activated!</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Your account has been set up successfully. You can now sign in with your credentials.
            </p>
            <Button onClick={() => navigate("/")} className="w-full">
              Go to Login
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-sm animate-scale-in">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
            <UserPlus className="w-6 h-6 text-primary" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">Set Up Account</h1>
        </div>

        {/* Card */}
        <div className="glass-card rounded-xl p-6">
          <div className="mb-6">
            <h2 className="text-lg font-medium mb-1">Welcome!</h2>
            <p className="text-sm text-muted-foreground">
              Complete your account setup for <span className="text-foreground">{userEmail}</span>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Full Name</label>
              <Input
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
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
                  minLength={8}
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

            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Confirm Password</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
              />
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
                "Activate Account"
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default InvitePage;
