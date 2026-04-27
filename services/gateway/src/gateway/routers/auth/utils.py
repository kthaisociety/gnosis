import os

def hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def get_admin_key() -> str:
    return os.getenv("ADMIN_API_KEY")
