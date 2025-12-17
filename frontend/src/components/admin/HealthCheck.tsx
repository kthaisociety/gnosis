import { useState, useEffect } from "react";
import { Activity, Database, Server, Cpu } from "lucide-react";

interface ServiceStatus {
  name: string;
  status: "live" | "down" | "degraded";
  latency?: number;
  icon: React.ReactNode;
}

const HealthCheck = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: "API Server", status: "live", latency: 45, icon: <Server className="w-4 h-4" /> },
    { name: "Database", status: "live", latency: 12, icon: <Database className="w-4 h-4" /> },
    { name: "OCR Engine", status: "live", latency: 230, icon: <Cpu className="w-4 h-4" /> },
    { name: "File Storage", status: "live", latency: 78, icon: <Activity className="w-4 h-4" /> },
  ]);

  // Simulate random status updates
  useEffect(() => {
    const interval = setInterval(() => {
      setServices(prev => prev.map(service => ({
        ...service,
        latency: Math.floor(Math.random() * 50) + (service.latency || 50) - 25,
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "live": return "bg-emerald-500";
      case "down": return "bg-destructive";
      case "degraded": return "bg-yellow-500";
      default: return "bg-muted";
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case "live": return "bg-emerald-500/10 border-emerald-500/20";
      case "down": return "bg-destructive/10 border-destructive/20";
      case "degraded": return "bg-yellow-500/10 border-yellow-500/20";
      default: return "bg-muted/10 border-muted/20";
    }
  };

  const allLive = services.every(s => s.status === "live");

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium">System Health</h3>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${getStatusBg(allLive ? "live" : "degraded")} border`}>
          <span className={`w-2 h-2 rounded-full ${getStatusColor(allLive ? "live" : "degraded")} animate-pulse`} />
          {allLive ? "All Systems Operational" : "Issues Detected"}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((service) => (
          <div
            key={service.name}
            className={`flex items-center justify-between p-4 rounded-lg border ${getStatusBg(service.status)}`}
          >
            <div className="flex items-center gap-3">
              <div className="text-muted-foreground">{service.icon}</div>
              <div>
                <p className="font-medium text-sm">{service.name}</p>
                <p className="text-xs text-muted-foreground">
                  {service.latency}ms latency
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor(service.status)} ${service.status === "live" ? "animate-pulse" : ""}`} />
              <span className="text-xs font-medium capitalize">{service.status}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground text-center">
          Last checked: {new Date().toLocaleTimeString()} • Auto-refresh every 5s
        </p>
      </div>
    </div>
  );
};

export default HealthCheck;
