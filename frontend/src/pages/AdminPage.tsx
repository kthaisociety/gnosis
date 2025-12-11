import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AdminLoginPage from "@/components/admin/AdminLoginPage";
import AdminNav from "@/components/admin/AdminNav";
import HealthCheck from "@/components/admin/HealthCheck";
import UserManagement from "@/components/admin/UserManagement";
import AdminBenchmark from "@/components/admin/AdminBenchmark";

const AdminDashboard = () => (
  <div className="p-6 md:p-8">
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Manage users and monitor system health</p>
      </div>
      <HealthCheck />
      <UserManagement />
    </div>
  </div>
);

const AdminPage = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  if (!isAuthenticated) {
    return <AdminLoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen flex flex-col">
      <AdminNav onLogout={() => setIsAuthenticated(false)} />
      <Routes>
        <Route index element={<AdminDashboard />} />
        <Route path="benchmark" element={<AdminBenchmark />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </div>
  );
};

export default AdminPage;
