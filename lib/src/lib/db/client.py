import os
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()

_pool = None


def get_db_pool():
    """Singleton pattern to ensure we only create one pool."""
    global _pool
    if _pool is None:
        conn_string = os.getenv("DATABASE_URL")
        # Create SINGLE pool for multiple concurrent connections
        _pool = ConnectionPool(conn_string, min_size=1, max_size=10)
    return _pool


def close_db_pool():
    """Call on app shutdown"""
    global _pool
    if _pool:
        _pool.close()
