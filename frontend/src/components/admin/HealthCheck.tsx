import { Server } from "lucide-react";
import { useHealth } from "@/hooks/useHealth";

const HealthCheck = () => {
  const { health, isOnline } = useHealth(10_000);

  const status = isOnline === null ? "loading" : isOnline ? "live" : "down";

  const getStatusColor = (s: string) => {
    switch (s) {
      case "live":    return "bg-emerald-500";
      case "down":    return "bg-destructive";
      case "loading": return "bg-muted";
      default:        return "bg-muted";
    }
  };

  const getStatusBg = (s: string) => {
    switch (s) {
      case "live":    return "bg-emerald-500/10 border-emerald-500/20";
      case "down":    return "bg-destructive/10 border-destructive/20";
      case "loading": return "bg-muted/10 border-muted/20";
      default:        return "bg-muted/10 border-muted/20";
    }
  };

  const statusLabel = status === "loading" ? "checking…" : status;

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium">System Health</h3>
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${getStatusBg(status)} border`}
        >
          <span
            className={`w-2 h-2 rounded-full ${getStatusColor(status)} ${status === "live" ? "animate-pulse" : ""}`}
          />
          {status === "live"
            ? "All Systems Operational"
            : status === "down"
            ? "API Offline"
            : "Checking…"}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div
          className={`flex items-center justify-between p-4 rounded-lg border ${getStatusBg(status)}`}
        >
          <div className="flex items-center gap-3">
            <div className="text-muted-foreground">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <p className="font-medium text-sm">API Server</p>
              <p className="text-xs text-muted-foreground">
                {health
                  ? `Uptime: ${health.uptime_human}`
                  : status === "loading"
                  ? "Connecting…"
                  : "Unreachable"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${getStatusColor(status)} ${status === "live" ? "animate-pulse" : ""}`}
            />
            <span className="text-xs font-medium capitalize">{statusLabel}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground text-center">
          {health
            ? `Last checked: ${health.last_checked_utc}`
            : "Polling every 10 s"}
          {" · "}Auto-refresh every 10s
        </p>
      </div>
    </div>
  );
};

export default HealthCheck;
