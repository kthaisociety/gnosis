import os
import hashlib


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def get_admin_key() -> str:
    return os.getenv("ADMIN_API_KEY")
