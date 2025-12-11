# RSS reading is a bit of a hack, but it's the only way to get the RSS of the process which we use for monitoring.
# It gives us a rough estimate of the memory usage of the process.
def get_rss_bytes() -> int:
    """
    Return resident set size (RSS) in bytes using /proc/self/status.
    Linux-only, O(1), no imports beyond stdlib.
    """
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    # e.g., "VmRSS:\t   123456 kB"
                    parts = line.split()
                    if len(parts) >= 3 and parts[-1].lower() == "kb":
                        return int(parts[-2]) * 1024
                    # fallback: try numeric part
                    for token in parts[1:]:
                        try:
                            return int(token) * 1024
                        except ValueError:
                            continue
    except Exception:
        pass
    return -1


def format_bytes(n: int) -> str:
    if n < 0:
        return "unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.1f} {u}"
        size /= 1024.0
    return f"{n} B"
