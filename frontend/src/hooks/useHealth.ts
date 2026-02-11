import { useState, useEffect } from "react";
import { getHealthStatus, type HealthStatus } from "@/lib/api";

export interface UseHealthResult {
  health: HealthStatus | null;
  /** null = still loading, true = API OK, false = offline / error */
  isOnline: boolean | null;
}

export function useHealth(pollIntervalMs = 10_000): UseHealthResult {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;

    const check = async () => {
      try {
        const data = await getHealthStatus();
        if (isMounted) {
          setHealth(data);
          setIsOnline(data.status === "OK");
        }
      } catch {
        if (isMounted) {
          setHealth(null);
          setIsOnline(false);
        }
      }
    };

    check();
    const id = setInterval(check, pollIntervalMs);
    return () => {
      isMounted = false;
      clearInterval(id);
    };
  }, [pollIntervalMs]);

  return { health, isOnline };
}
