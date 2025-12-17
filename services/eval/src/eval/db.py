from psycopg.sql import Identifier, SQL
from dotenv import load_dotenv

from lib.utils.log import get_logger
from lib.db import get_db_pool

load_dotenv()
logger = get_logger(__name__)


def create_dataset(dataset_name: str):
    pool = get_db_pool()
    sql = SQL(
        """CREATE TABLE IF NOT EXISTS {} (
            id SERIAL PRIMARY KEY,
            image_path TEXT NOT NULL,
            image_type VARCHAR(50) NOT NULL,
            expected TEXT NOT NULL
        )
        """
    ).format(Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
