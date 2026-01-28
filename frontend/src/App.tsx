import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route, useNavigate, Link } from "react-router-dom";
import { NeonAuthUIProvider } from "@neondatabase/neon-js/auth/react";
import { authClient } from "@/lib/auth";
import Index from "./pages/Index";
import AdminPage from "./pages/AdminPage";
import InvitePage from "./pages/InvitePage";
import LoginPage from "./components/LoginPage";
import Account from "./pages/Account";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Create a wrapper for Link to match NeonAuthUIProvider's expected props
const CustomLink = ({ href, children, ...props }: any) => {
  return (
    <Link to={href} {...props}>
      {children}
    </Link>
  );
};

const App = () => {
  const navigate = useNavigate();

  return (
    <QueryClientProvider client={queryClient}>
      <NeonAuthUIProvider
        authClient={authClient}
        navigate={navigate}
        Link={CustomLink}
        credentials={{ forgotPassword: true }}
        social={{ providers: ["google"] }}
      >
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Index />} />
              <Route path="/account/:view" element={<Account />} />
            </Route>
            <Route element={<AdminRoute />}>
              <Route path="/admin/*" element={<AdminPage />} />
            </Route>
            <Route path="/invite/:token" element={<InvitePage />} />
            <Route path="/auth/:view" element={<LoginPage />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </TooltipProvider>
      </NeonAuthUIProvider>
    </QueryClientProvider>
  );
};

export default App;
