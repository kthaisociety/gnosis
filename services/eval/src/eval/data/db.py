from psycopg.sql import Identifier, SQL
from psycopg.rows import dict_row
from dotenv import load_dotenv
from typing import List

from lib.utils.log import get_logger
from lib.db import get_db_pool, drop_table
from eval.models import EvalDatasetItem, EvalOutput

load_dotenv()
logger = get_logger(__name__)


def create_dataset(dataset_name: str):
    pool = get_db_pool()
    sql = SQL(
        """CREATE TABLE IF NOT EXISTS datasets.{} (
            id SERIAL PRIMARY KEY,
            image_path TEXT UNIQUE NOT NULL,
            output_schema_name VARCHAR(50) NOT NULL,
            expected TEXT NOT NULL
        )
        """
    ).format(Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def get_dataset_items(dataset_name: str) -> List[EvalDatasetItem]:
    pool = get_db_pool()
    sql = SQL("SELECT * FROM datasets.{}").format(Identifier(dataset_name))
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [EvalDatasetItem(**row) for row in rows]


def upsert_dataset(dataset_name: str, model: EvalDatasetItem):
    pool = get_db_pool()
    data = model.model_dump()

    sql = SQL(
        """INSERT INTO datasets.{} (image_path, output_schema_name, expected)
        VALUES (%(image_path)s, %(output_schema_name)s, %(expected)s)
        ON CONFLICT (image_path) DO UPDATE SET
            output_schema_name = EXCLUDED.output_schema_name,
            expected = EXCLUDED.expected
        """
    ).format(Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, data)


def drop_dataset(dataset_name: str):
    pool = get_db_pool()
    sql = SQL("DROP TABLE IF EXISTS datasets.{}").format(
        Identifier(dataset_name))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql)
                return True
            except Exception as e:
                logger.error(f"Failed to drop dataset named {
                             dataset_name}: {e}")
                return False


def create_eval_table():
    pool = get_db_pool()
    sql = SQL(
        """CREATE TABLE IF NOT EXISTS eval (
            id SERIAL PRIMARY KEY,
            model_name TEXT NOT NULL,
            dataset_name VARCHAR(50) NOT NULL,
            output_schema_name VARCHAR(50) NOT NULL,
            avg_rnss FLOAT4 NOT NULL,
            avg_rms FLOAT4 NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (model_name, dataset_name, output_schema_name)
        )
        """
    )

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def get_eval_items() -> List[EvalOutput]:
    pool = get_db_pool()
    sql = SQL("SELECT * FROM eval")
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [EvalOutput(**row) for row in rows]


def upsert_eval_table(model: EvalOutput):
    pool = get_db_pool()
    data = model.model_dump()

    sql = SQL(
        """INSERT INTO eval (model_name, dataset_name, output_schema_name, avg_rnss, avg_rms)
        VALUES (%(model_name)s, %(dataset_name)s, %(output_schema_name)s, %(avg_rnss)s, %(avg_rms)s)
        ON CONFLICT (model_name, dataset_name, output_schema_name) DO UPDATE SET
            avg_rnss = EXCLUDED.avg_rnss,
            avg_rms = EXCLUDED.avg_rms,
            updated_at = NOW()
        """
    )

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, data)


def drop_eval_table():
    drop_table("eval")
