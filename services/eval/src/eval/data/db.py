"""
Database operations for the VLM Benchmark schema.
Handles datasets, images, evaluation runs, predictions, and metrics.
"""

from psycopg.sql import SQL, Identifier
from psycopg.rows import dict_row
from psycopg import errors
from typing import List, Optional
from dotenv import load_dotenv
from uuid import UUID
import json
import os
from lib.utils.log import get_logger
from lib.db import get_db_pool
from eval.models import (
    Dataset,
    DatasetCreate,
    Image,
    ImageCreate,
    ImageStatus,
    EvaluationRun,
    EvaluationRunCreate,
    RunStatus,
    Prediction,
    PredictionCreate,
    Metric,
    MetricCreate,
)

logger = get_logger(__name__)


load_dotenv()
SCHEMA_NAME = os.getenv("SCHEMA_NAME")


def create_dataset(dataset: DatasetCreate) -> Optional[UUID]:
    """
    Creates a new dataset.

    Args:
        dataset: Dataset creation data

    Returns:
        UUID of created dataset, or None if creation failed
    """
    pool = get_db_pool()
    sql = SQL("""
        INSERT INTO {schema}.datasets (name, description, version)
        VALUES (%(name)s, %(description)s, %(version)s)
        RETURNING dataset_id
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, dataset.model_dump())
                result = cur.fetchone()
                dataset_id = result[0] if result else None
                logger.info(f"Created dataset '{dataset.name}' with ID: {dataset_id}")
                return dataset_id
    except errors.UniqueViolation:
        logger.error(f"Dataset with name '{dataset.name}' already exists")
        return None
    except Exception as e:
        logger.error(f"Failed to create dataset: {e}")
        return None


def get_dataset(dataset_id: UUID) -> Optional[Dataset]:
    """
    Retrieves a dataset by ID.

    Args:
        dataset_id: UUID of the dataset

    Returns:
        Dataset object or None if not found
    """
    pool = get_db_pool()
    sql = SQL("SELECT * FROM {schema}.datasets WHERE dataset_id = %s").format(
        schema=Identifier(SCHEMA_NAME)
    )

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (dataset_id,))
                row = cur.fetchone()
                return Dataset(**row) if row else None
    except Exception as e:
        logger.error(f"Failed to get dataset {dataset_id}: {e}")
        return None


def get_dataset_by_name(name: str) -> Optional[Dataset]:
    """
    Retrieves a dataset by name.

    Args:
        name: Name of the dataset

    Returns:
        Dataset object or None if not found
    """
    pool = get_db_pool()
    sql = SQL("SELECT * FROM {schema}.datasets WHERE name = %s").format(
        schema=Identifier(SCHEMA_NAME)
    )

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (name,))
                row = cur.fetchone()
                return Dataset(**row) if row else None
    except Exception as e:
        logger.error(f"Failed to get dataset by name '{name}': {e}")
        return None


def list_datasets() -> List[Dataset]:
    """
    Lists all datasets.

    Returns:
        List of Dataset objects
    """
    pool = get_db_pool()
    sql = SQL("SELECT * FROM {schema}.datasets ORDER BY created_at DESC").format(
        schema=Identifier(SCHEMA_NAME)
    )

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                return [Dataset(**row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        return []


# Image operations


def create_image(image: ImageCreate) -> Optional[UUID]:
    """
    Creates a new image record.

    Args:
        image: Image creation data

    Returns:
        UUID of created image, or None if creation failed
    """
    pool = get_db_pool()
    sql = SQL("""
        INSERT INTO {schema}.images
        (dataset_id, file_path, s3_etag, width, height, format,
         file_size_bytes, image_type, metadata, ground_truth)
        VALUES (
            %(dataset_id)s, %(file_path)s, %(s3_etag)s, %(width)s, %(height)s,
            %(format)s, %(file_size_bytes)s, %(image_type)s, %(metadata)s, %(ground_truth)s
        )
        RETURNING image_id
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                data = image.model_dump()
                # Convert dicts to JSON strings for JSONB columns
                data["metadata"] = json.dumps(data["metadata"])
                data["ground_truth"] = (
                    json.dumps(data["ground_truth"]) if data["ground_truth"] else None
                )

                cur.execute(sql, data)
                result = cur.fetchone()
                image_id = result[0] if result else None
                logger.info(f"Created image with ID: {image_id}")
                return image_id
    except Exception as e:
        logger.error(f"Failed to create image: {e}")
        return None


def get_image(image_id: UUID) -> Optional[Image]:
    """
    Retrieves an image by ID.

    Args:
        image_id: UUID of the image

    Returns:
        Image object or None if not found
    """
    pool = get_db_pool()
    sql = SQL("SELECT * FROM {schema}.images WHERE image_id = %s").format(
        schema=Identifier(SCHEMA_NAME)
    )

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (image_id,))
                row = cur.fetchone()
                return Image(**row) if row else None
    except Exception as e:
        logger.error(f"Failed to get image {image_id}: {e}")
        return None


def update_image_status(
    image_id: UUID, status: ImageStatus, s3_etag: Optional[str] = None
) -> bool:
    """
    Updates the status of an image.

    Args:
        image_id: UUID of the image
        status: New status
        s3_etag: Optional S3 ETag to update

    Returns:
        True if update was successful, False otherwise
    """
    pool = get_db_pool()

    if s3_etag:
        sql = SQL("""
            UPDATE {schema}.images
            SET status = %s, s3_etag = %s, updated_at = NOW()
            WHERE image_id = %s
        """).format(schema=Identifier(SCHEMA_NAME))
        params = (status.value, s3_etag, image_id)
    else:
        sql = SQL("""
            UPDATE {schema}.images
            SET status = %s, updated_at = NOW()
            WHERE image_id = %s
        """).format(schema=Identifier(SCHEMA_NAME))
        params = (status.value, image_id)

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return True
    except Exception as e:
        logger.error(f"Failed to update image status: {e}")
        return False


def list_images_by_dataset(
    dataset_id: UUID, status: Optional[ImageStatus] = None
) -> List[Image]:
    """
    Lists all images in a dataset.

    Args:
        dataset_id: UUID of the dataset
        status: Optional status filter

    Returns:
        List of Image objects
    """
    pool = get_db_pool()

    if status:
        sql = SQL("""
            SELECT * FROM {schema}.images
            WHERE dataset_id = %s AND status = %s
            ORDER BY created_at DESC
        """).format(schema=Identifier(SCHEMA_NAME))
        params = (dataset_id, status.value)
    else:
        sql = SQL("""
            SELECT * FROM {schema}.images
            WHERE dataset_id = %s
            ORDER BY created_at DESC
        """).format(schema=Identifier(SCHEMA_NAME))
        params = (dataset_id,)

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                return [Image(**row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to list images: {e}")
        return []


def create_evaluation_run(run: EvaluationRunCreate) -> Optional[UUID]:
    """
    Creates a new evaluation run.

    Args:
        run: Evaluation run creation data

    Returns:
        UUID of created run, or None if creation failed
    """
    pool = get_db_pool()
    sql = SQL("""
        INSERT INTO {schema}.evaluation_runs
        (model_name, model_version, dataset_id, dataset_version, config, initiated_by)
        VALUES (%(model_name)s, %(model_version)s, %(dataset_id)s,
                %(dataset_version)s, %(config)s, %(initiated_by)s)
        RETURNING run_id
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                data = run.model_dump()
                data["config"] = json.dumps(data["config"])

                cur.execute(sql, data)
                result = cur.fetchone()
                run_id = result[0] if result else None
                logger.info(f"Created evaluation run with ID: {run_id}")
                return run_id
    except Exception as e:
        logger.error(f"Failed to create evaluation run: {e}")
        return None


def update_run_status(
    run_id: UUID,
    status: RunStatus,
    error_message: Optional[str] = None,
    total_images: Optional[int] = None,
    processed_images: Optional[int] = None,
    failed_images: Optional[int] = None,
) -> bool:
    """
    Updates the status and progress of an evaluation run.

    Args:
        run_id: UUID of the run
        status: New status
        error_message: Optional error message
        total_images: Optional total images count
        processed_images: Optional processed images count
        failed_images: Optional failed images count

    Returns:
        True if update was successful, False otherwise
    """
    pool = get_db_pool()

    updates = ["status = %s"]
    params = [status.value]

    if error_message is not None:
        updates.append("error_message = %s")
        params.append(error_message)

    if total_images is not None:
        updates.append("total_images = %s")
        params.append(total_images)

    if processed_images is not None:
        updates.append("processed_images = %s")
        params.append(processed_images)

    if failed_images is not None:
        updates.append("failed_images = %s")
        params.append(failed_images)

    if status == RunStatus.RUNNING:
        updates.append("started_at = NOW()")
    elif status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
        updates.append("completed_at = NOW()")

    params.append(run_id)

    sql = SQL(f"""
        UPDATE {{schema}}.evaluation_runs
        SET {', '.join(updates)}
        WHERE run_id = %s
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return True
    except Exception as e:
        logger.error(f"Failed to update run status: {e}")
        return False


def get_evaluation_run(run_id: UUID) -> Optional[EvaluationRun]:
    """
    Retrieves an evaluation run by ID.

    Args:
        run_id: UUID of the run

    Returns:
        EvaluationRun object or None if not found
    """
    pool = get_db_pool()
    sql = SQL("SELECT * FROM {schema}.evaluation_runs WHERE run_id = %s").format(
        schema=Identifier(SCHEMA_NAME)
    )

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (run_id,))
                row = cur.fetchone()
                return EvaluationRun(**row) if row else None
    except Exception as e:
        logger.error(f"Failed to get evaluation run {run_id}: {e}")
        return None


# prediction operations


def create_prediction(prediction: PredictionCreate) -> Optional[UUID]:
    """
    Creates a new prediction record.

    Args:
        prediction: Prediction creation data

    Returns:
        UUID of created prediction, or None if creation failed
    """
    pool = get_db_pool()
    sql = SQL("""
        INSERT INTO {schema}.predictions
        (image_id, run_id, output, raw_response, latency_ms,
         input_tokens, output_tokens, success, error_message)
        VALUES (%(image_id)s, %(run_id)s, %(output)s, %(raw_response)s,
                %(latency_ms)s, %(input_tokens)s, %(output_tokens)s,
                %(success)s, %(error_message)s)
        RETURNING prediction_id
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                data = prediction.model_dump()
                data["output"] = json.dumps(data["output"]) if data["output"] else None

                cur.execute(sql, data)
                result = cur.fetchone()
                prediction_id = result[0] if result else None
                logger.info(f"Created prediction with ID: {prediction_id}")
                return prediction_id
    except Exception as e:
        logger.error(f"Failed to create prediction: {e}")
        return None


def get_predictions_by_run(run_id: UUID) -> List[Prediction]:
    """
    Retrieves all predictions for an evaluation run.

    Args:
        run_id: UUID of the run

    Returns:
        List of Prediction objects
    """
    pool = get_db_pool()
    sql = SQL("""
        SELECT * FROM {schema}.predictions
        WHERE run_id = %s
        ORDER BY created_at
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (run_id,))
                rows = cur.fetchall()
                return [Prediction(**row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get predictions for run {run_id}: {e}")
        return []


# metric operations


def create_metric(metric: MetricCreate) -> Optional[UUID]:
    """
    Creates a new metric record.

    Args:
        metric: Metric creation data

    Returns:
        UUID of created metric, or None if creation failed
    """
    pool = get_db_pool()
    sql = SQL("""
        INSERT INTO {schema}.metrics
        (prediction_id, metric_name, metric_value, meta_data)
        VALUES (%(prediction_id)s, %(metric_name)s, %(metric_value)s, %(meta_data)s)
        RETURNING metric_id
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                data = metric.model_dump()
                data["meta_data"] = json.dumps(data["meta_data"])

                cur.execute(sql, data)
                result = cur.fetchone()
                metric_id = result[0] if result else None
                return metric_id
    except Exception as e:
        logger.error(f"Failed to create metric: {e}")
        return None


def get_metrics_by_prediction(prediction_id: UUID) -> List[Metric]:
    """
    Retrieves all metrics for a prediction.

    Args:
        prediction_id: UUID of the prediction

    Returns:
        List of Metric objects
    """
    pool = get_db_pool()
    sql = SQL("""
        SELECT * FROM {schema}.metrics
        WHERE prediction_id = %s
        ORDER BY metric_name
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (prediction_id,))
                rows = cur.fetchall()
                return [Metric(**row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get metrics for prediction {prediction_id}: {e}")
        return []


def get_run_metrics_summary(run_id: UUID) -> dict:
    """
    Calculates aggregate metrics for an evaluation run.

    Args:
        run_id: UUID of the run

    Returns:
        Dictionary with metric statistics (avg, min, max per metric type)
    """
    pool = get_db_pool()
    sql = SQL("""
        SELECT
            m.metric_name,
            AVG(m.metric_value) as avg_value,
            MIN(m.metric_value) as min_value,
            MAX(m.metric_value) as max_value,
            COUNT(*) as count
        FROM {schema}.metrics m
        JOIN {schema}.predictions p ON m.prediction_id = p.prediction_id
        WHERE p.run_id = %s
        GROUP BY m.metric_name
    """).format(schema=Identifier(SCHEMA_NAME))

    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, (run_id,))
                rows = cur.fetchall()
                return {row["metric_name"]: dict(row) for row in rows}
    except Exception as e:
        logger.error(f"Failed to get metrics summary for run {run_id}: {e}")
        return {}
