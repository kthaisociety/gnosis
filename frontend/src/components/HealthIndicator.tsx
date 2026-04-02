import { Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import type { UseHealthResult } from "@/hooks/useHealth";

interface HealthIndicatorProps {
  health: UseHealthResult;
}

const HealthIndicator = ({
  health: { isOnline, health },
}: HealthIndicatorProps) => {
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <Activity className="w-3.5 h-3.5" />
      <div className="flex items-center gap-1.5">
        <span
          className={cn(
            "inline-block w-2 h-2 rounded-full transition-colors",
            isOnline === null && "bg-muted-foreground animate-pulse",
            isOnline === true && "bg-green-500 animate-pulse",
            isOnline === false && "bg-red-500",
          )}
        />
        <span>
          {isOnline === null
            ? "Checking…"
            : isOnline
              ? "API Online"
              : "API Offline"}
        </span>
      </div>
    </div>
  );
};

export default HealthIndicator;
