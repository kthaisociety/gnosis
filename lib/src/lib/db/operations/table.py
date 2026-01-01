from psycopg.sql import SQL, Identifier

from ..client import get_db_pool
from lib.utils.log import get_logger

logger = get_logger(__name__)


def drop_table(table_name: str) -> bool:
    pool = get_db_pool()
    sql = SQL("DROP TABLE IF EXISTS {}").format(Identifier(table_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql)
                return True
            except Exception as e:
                logger.error(f"Failed to drop table named {table_name}: {e}")
                return False
