import requests
from typing import Optional


def health(url: str) -> bool:
    """Check if gateway is healthy."""
    try:
        res = requests.get(f"{url}/health", timeout=5)
        return res.status_code == 200
    except Exception:
        return False


def auth(url: str, api_key: str) -> bool:
    """Verify API key works."""
    headers = {"X-API-Key": api_key}
    try:
        res = requests.get(f"{url}/auth", headers=headers, timeout=5)
        return res.status_code == 200
    except Exception:
        return False


def process(url: str, api_key: str, image_path: str, config: dict) -> Optional[dict]:
    """Send image for processing."""
    headers = {"X-API-Key": api_key}

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"runner": "modal", "config": str(config)}
            res = requests.post(
                f"{url}/process",
                headers=headers,
                files=files,
                data=data,
                timeout=120,
            )
        if res.status_code == 200:
            return res.json()
        return None
    except Exception:
        return None


def create_api_key(
    url: str, admin_key: str, name: str, expires_in_days: int = None
) -> Optional[str]:
    """Create new API key. Requires admin key."""
    headers = {"X-Admin-Key": admin_key}
    data = {"name": name}
    if expires_in_days:
        data["expires_in_days"] = expires_in_days

    try:
        res = requests.post(f"{url}/auth/keys", headers=headers, json=data, timeout=5)
        if res.status_code == 200:
            return res.json().get("key")
        return None
    except Exception:
        return None
