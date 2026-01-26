from psycopg.sql import SQL, Identifier

from ..client import get_db_pool
from lib.utils.log import get_logger

logger = get_logger(__name__)


def create_schema(name: str) -> bool:
    pool = get_db_pool()
    sql = SQL("CREATE SCHEMA IF NOT EXISTS {}").format(Identifier(name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql)
                return True
            except Exception as e:
                logger.error(f"Failed to create schema named {name}: {e}")
                return False


def drop_schema(name: str) -> bool:
    pool = get_db_pool()
    sql = SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(Identifier(name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql)
                return True
            except Exception as e:
                logger.error(f"Failed to drop schema named {name}: {e}")
                return False
