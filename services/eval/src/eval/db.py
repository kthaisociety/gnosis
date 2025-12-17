from psycopg.sql import Identifier, SQL
from dotenv import load_dotenv

from lib.utils.log import get_logger
from lib.db import get_db_pool
from .models import EvalDatasetItem

load_dotenv()
logger = get_logger(__name__)


def create_dataset(dataset_name: str):
    pool = get_db_pool()
    sql = SQL(
        """CREATE TABLE IF NOT EXISTS datasets.{} (
            id SERIAL PRIMARY KEY,
            image_path TEXT UNIQUE NOT NULL,
            image_type VARCHAR(50) NOT NULL,
            expected TEXT NOT NULL
        )
        """
    ).format(Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def upsert_dataset(dataset_name: str, model: EvalDatasetItem):
    pool = get_db_pool()
    data = model.model_dump()

    sql = SQL(
        """INSERT INTO datasets.{} (image_path, image_type, expected)
        VALUES (%(image_path)s, %(image_type)s, %(expected)s)
        ON CONFLICT (image_path) DO UPDATE SET
            image_type = EXCLUDED.image_type,
            expected = EXCLUDED.expected
        """
    ).format(Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, data)


def drop_dataset(dataset_name: str):
    pool = get_db_pool()
    sql = SQL("DROP TABLE IF EXISTS datasets.{}").format(Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql)
                return True
            except Exception as e:
                logger.error(f"Failed to drop dataset named {dataset_name}: {e}")
                return False
