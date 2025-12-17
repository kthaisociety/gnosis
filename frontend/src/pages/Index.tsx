import { useState } from "react";
import LoginPage from "@/components/LoginPage";
import BenchmarkCard from "@/components/BenchmarkCard";

const Index = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  return <BenchmarkCard onLogout={() => setIsAuthenticated(false)} />;
};

export default Index;
