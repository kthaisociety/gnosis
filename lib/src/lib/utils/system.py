# RSS reading is a bit of a hack, but it's the only way to get the RSS of the process which we use for monitoring.
# It gives us a rough estimate of the memory usage of the process.
def get_rss_bytes() -> int:
    """Return RSS in bytes from /proc/self/status. (Linux)"""
    try:
        with open("/proc/self/status") as f:
            # Find the line efficiently without reading the whole file
            line = next((l for l in f if l.startswith("VmRSS:")), "")

        parts = line.split()
        # 1. Standard format check: "VmRSS: 1234 kB"
        if len(parts) >= 3 and parts[-1].lower() == "kb":
            return int(parts[-2]) * 1024

        # 2. Fallback: Find first digit string (Preserves your original loop logic)
        return int(next(p for p in parts[1:] if p.isdigit())) * 1024
    except Exception:
        return -1


def format_bytes(n: int) -> str:
    if n < 0:
        return "unknown"
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024 or u == "TB":
            return f"{n:.1f} {u}"
        n /= 1024
