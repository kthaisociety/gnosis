import { AuthView } from "@neondatabase/neon-js/auth/react/ui";
import { useParams } from "react-router-dom";
import { Eye, EyeOff, Scan, Shield } from "lucide-react";


export function LoginPage() {
  const { view } = useParams();

  if (view === "sign-up") {
    return (
      
      <div
        style={{
          display: "flex",
          flexDirection: "column",    
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
        }}
      >
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
            <Scan className="w-6 h-6 text-primary" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">OCR Bench</h1>
        </div>
        <p>Contact admin - signup on invite only</p>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
      }}
    >
      <div className="flex items-center justify-center gap-3 mb-8">
        <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
          <Scan className="w-6 h-6 text-primary" />
        </div>
        <h1 className="text-xl font-semibold tracking-tight">OCR Bench</h1>
      </div>
      <p className="text-sm text-muted-foreground mb-4">Hint: Use your kthais email to login</p>
      <div className="w-full max-w-sm">
        <AuthView 
          pathname={view === "sign-up" ? "sign-up" : "sign-in"} 
        />
      </div>
    </div>
  );
}

export default LoginPage;
