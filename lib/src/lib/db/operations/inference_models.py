# CRUD operations for neondb
import json
from typing import List, Optional

from lib.db.client import get_db_pool
from lib.models.vlm import Infer


CRUD_COLUMNS = """
    model_name, inference_type, inference_class, requires_gpu,
    default_config, version, multimodal,
    avg_latency, top_percentile_accuracy,
    latest_eval_accuracy, latest_eval_datetime
"""


def _row_to_infer(row: tuple) -> Optional[Infer]:
    """Converts a database row to an Infer model."""
    if not row:
        return None

    (
        model_name,
        inference_type,
        inference_class,
        requires_gpu,
        default_config,
        version,
        multimodal,
        avg_latency,
        top_percentile_accuracy,
        latest_eval_accuracy,
        latest_eval_datetime,
    ) = row

    return Infer(
        model_name=model_name,
        inference_type=inference_type,
        inference_class=inference_class,
        requires_gpu=requires_gpu,
        default_config=default_config,
        version=version,
        multimodal=multimodal,
        avg_latency=avg_latency,
        top_percentile_accuracy=top_percentile_accuracy,
        latest_eval_accuracy=latest_eval_accuracy,
        latest_eval_datetime=latest_eval_datetime,
    )


def create_inference_model(model: Infer) -> Optional[Infer]:
    """Creates a new inference model record."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO inference_models ({CRUD_COLUMNS}) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            f"RETURNING {CRUD_COLUMNS};",
            (
                model.model_name,
                model.inference_type,
                model.inference_class,
                model.requires_gpu,
                json.dumps(model.default_config),
                model.version,
                model.multimodal,
                model.avg_latency,
                model.top_percentile_accuracy,
                model.latest_eval_accuracy,
                model.latest_eval_datetime,
            ),
        )
        return _row_to_infer(cur.fetchone())


def get_inference_model(model_name: str, version: int) -> Optional[Infer]:
    """Retrieves an inference model by name and version."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT {CRUD_COLUMNS} FROM inference_models "
            "WHERE model_name = %s AND version = %s;",
            (model_name, version),
        )
        return _row_to_infer(cur.fetchone())


def get_all_inference_models() -> List[Infer]:
    """Retrieves all inference models."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT {CRUD_COLUMNS} FROM inference_models;")
        return [_row_to_infer(row) for row in cur.fetchall() if row]


def update_inference_model(
    model_name: str, version: int, model: Infer
) -> Optional[Infer]:
    """Updates an existing inference model."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE inference_models
            SET model_name = %s, inference_type = %s, inference_class = %s,
                requires_gpu = %s, default_config = %s,
                version = %s, multimodal = %s,
                avg_latency = %s, top_percentile_accuracy = %s,
                latest_eval_accuracy = %s, latest_eval_datetime = %s
            WHERE model_name = %s AND version = %s
            RETURNING {CRUD_COLUMNS};
            """,
            (
                model.model_name,
                model.inference_type,
                model.inference_class,
                model.requires_gpu,
                json.dumps(model.default_config),
                model.version,
                model.multimodal,
                model.avg_latency,
                model.top_percentile_accuracy,
                model.latest_eval_accuracy,
                model.latest_eval_datetime,
                model_name,  # for WHERE clause
                version,  # for WHERE clause
            ),
        )
        return _row_to_infer(cur.fetchone())


def delete_inference_model(model_name: str, version: int) -> bool:
    """Deletes an inference model."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM inference_models WHERE model_name = %s AND version = %s;",
            (model_name, version),
        )
        return cur.rowcount > 0


def upsert_inference_model(model: Infer) -> Optional[Infer]:
    """Upserts an inference model based on model_name and version."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO inference_models ({CRUD_COLUMNS})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (model_name, version) DO UPDATE SET
                inference_type = EXCLUDED.inference_type,
                inference_class = EXCLUDED.inference_class,
                requires_gpu = EXCLUDED.requires_gpu,
                default_config = EXCLUDED.default_config,
                multimodal = EXCLUDED.multimodal
            RETURNING {CRUD_COLUMNS};
            """,
            (
                model.model_name,
                model.inference_type,
                model.inference_class,
                model.requires_gpu,
                json.dumps(model.default_config),
                model.version,
                model.multimodal,
                model.avg_latency,
                model.top_percentile_accuracy,
                model.latest_eval_accuracy,
                model.latest_eval_datetime,
            ),
        )
        return _row_to_infer(cur.fetchone())


def ensure_inference_models_table_exists():
    """Creates the inference_models table if it doesn't exist."""
    pool = get_db_pool()
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS inference_models (
                id SERIAL PRIMARY KEY,
                model_name TEXT NOT NULL,
                inference_type TEXT,
                inference_class TEXT,
                requires_gpu BOOLEAN,
                default_config JSONB,
                version INTEGER NOT NULL,
                multimodal BOOLEAN NOT NULL,
                avg_latency FLOAT,
                top_percentile_accuracy FLOAT,
                latest_eval_accuracy FLOAT,
                latest_eval_datetime TIMESTAMP WITH TIME ZONE,
                UNIQUE (model_name, version)
            );
            """
        )
