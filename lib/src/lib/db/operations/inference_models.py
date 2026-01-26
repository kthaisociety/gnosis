# CRUD operations for neondb
import json
from typing import List, Optional

from lib.db.client import get_db_pool
from lib.models.vlm_models import Infer


CRUD_COLUMNS = """
    model_name, inference_type, inference_class, requires_gpu,
    default_prompt_name, default_config, version, multimodal,
    max_len_tokens, avg_latency, top_percentile_accuracy,
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
        default_prompt_name,
        default_config,
        version,
        multimodal,
        max_len_tokens,
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
        default_prompt_name=default_prompt_name,
        default_config=default_config,
        version=version,
        multimodal=multimodal,
        max_len_tokens=max_len_tokens,
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
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            f"RETURNING {CRUD_COLUMNS};",
            (
                model.model_name,
                model.inference_type,
                model.inference_class,
                model.requires_gpu,
                model.default_prompt_name,
                json.dumps(model.default_config),
                model.version,
                model.multimodal,
                model.max_len_tokens,
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
                requires_gpu = %s, default_prompt_name = %s, default_config = %s,
                version = %s, multimodal = %s, max_len_tokens = %s,
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
                model.default_prompt_name,
                json.dumps(model.default_config),
                model.version,
                model.multimodal,
                model.max_len_tokens,
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
