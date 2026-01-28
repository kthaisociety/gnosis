"""
Image upload pipeline: Local File → S3 (Cloudflare R2) → Neon Database

This module provides high-level functions to manage the complete workflow
of uploading benchmark images with UUID-based tracking.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID

from dotenv import load_dotenv
from lib.utils.log import get_logger
from eval.models import ImageCreate, ImageStatus
from .s3_bucket import (
    generate_s3_key,
    upload_image_to_s3,
    get_image_metadata,
    ensure_s3_bucket_exists,
)
from .db import update_image_status, get_image

load_dotenv()
logger = get_logger(__name__)

# Get schema name from environment
SCHEMA_NAME = os.getenv("SCHEMA_NAME", "benchmark")


def upload_benchmark_image(
    local_file_path: str,
    dataset_id: UUID,
    dataset_name: str,
    image_type: Optional[str] = None,
    ground_truth: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[UUID]:
    """
    Complete pipeline to upload a benchmark image.

    Workflow:
    1. Generate UUID for the image
    2. Create S3 key based on dataset and UUID
    3. Extract image metadata (dimensions, format, size)
    4. Create database record with status='pending_upload'
    5. Upload to S3
    6. Update database record with status='active' and ETag

    Args:
        local_file_path: Path to local image file
        dataset_id: UUID of the dataset this image belongs to
        dataset_name: Name of the dataset (used for S3 path)
        image_type: Optional classification (e.g., 'bar_chart', 'line_graph')
        ground_truth: Optional ground truth data (JSONB)
        metadata: Optional additional metadata (JSONB)

    Returns:
        UUID of the created image, or None if upload failed

    Example:
        ```python
        image_id = upload_benchmark_image(
            local_file_path="/path/to/chart.png",
            dataset_id=dataset_uuid,
            dataset_name="technical_charts_v1",
            image_type="bar_chart",
            ground_truth={"values": [1, 2, 3]},
            metadata={"source": "manual_upload"}
        )
        ```
    """
    try:
        # Ensure S3 bucket exists
        if not ensure_s3_bucket_exists():
            logger.error("S3 bucket does not exist and could not be created")
            return None

        # Get file extension
        file_ext = Path(local_file_path).suffix.lstrip(".")

        # Generate UUID and S3 key
        image_uuid, s3_key = generate_s3_key(dataset_name, file_ext)
        logger.info(f"Generated UUID {image_uuid} for image: {local_file_path}")

        # Extract image metadata
        img_metadata = get_image_metadata(local_file_path)

        # Merge with user-provided metadata
        if metadata is None:
            metadata = {}
        metadata.update(
            {
                "original_filename": Path(local_file_path).name,
                "upload_source": "pipeline",
            }
        )

        # Create database record with pending status
        image_data = ImageCreate(
            dataset_id=dataset_id,
            file_path=s3_key,
            width=img_metadata["width"],
            height=img_metadata["height"],
            format=img_metadata["format"],
            file_size_bytes=img_metadata["file_size_bytes"],
            image_type=image_type,
            metadata=metadata,
            ground_truth=ground_truth,
        )

        # We need to create the record with the specific UUID
        # This requires a custom insert
        from lib.db import get_db_pool
        from psycopg.sql import SQL, Identifier
        import json

        pool = get_db_pool()
        sql = SQL("""
            INSERT INTO {schema}.images
            (image_id, dataset_id, file_path, status, width, height, format,
             file_size_bytes, image_type, metadata, ground_truth)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING image_id
        """).format(schema=Identifier(SCHEMA_NAME))

        with pool.connection() as conn:
            with conn.cursor() as cur:
                data = image_data.model_dump()
                data["metadata"] = json.dumps(data["metadata"])
                data["ground_truth"] = (
                    json.dumps(data["ground_truth"]) if data["ground_truth"] else None
                )

                cur.execute(
                    sql,
                    (
                        image_uuid,
                        data["dataset_id"],
                        data["file_path"],
                        ImageStatus.PENDING_UPLOAD.value,
                        data["width"],
                        data["height"],
                        data["format"],
                        data["file_size_bytes"],
                        data["image_type"],
                        data["metadata"],
                        data["ground_truth"],
                    ),
                )

                result = cur.fetchone()
                created_image_id = result[0] if result else None

        if not created_image_id:
            logger.error("Failed to create database record for image")
            return None

        logger.info(f"Created database record for image {created_image_id}")

        # Upload to S3
        etag = upload_image_to_s3(local_file_path, s3_key)

        if etag:
            # Update status to active
            if update_image_status(created_image_id, ImageStatus.ACTIVE, etag):
                logger.info(f"Successfully uploaded image {created_image_id}")
                return created_image_id
            else:
                logger.error("Uploaded to S3 but failed to update database status")
                return created_image_id
        else:
            # Upload failed, update status
            update_image_status(created_image_id, ImageStatus.UPLOAD_FAILED)
            logger.error("Failed to upload image to S3")
            return None

    except Exception as e:
        logger.error(f"Error in upload pipeline: {e}")
        return None


def bulk_upload_images(
    image_files: list[str],
    dataset_id: UUID,
    dataset_name: str,
    image_type: Optional[str] = None,
) -> Dict[str, list[UUID]]:
    """
    Uploads multiple images to a dataset.

    Args:
        image_files: List of local file paths
        dataset_id: UUID of the dataset
        dataset_name: Name of the dataset
        image_type: Optional image type for all images

    Returns:
        Dictionary with 'successful' and 'failed' lists of UUIDs/paths
    """
    results = {"successful": [], "failed": []}

    logger.info(
        f"Starting bulk upload of {len(image_files)} images to dataset '{dataset_name}'"
    )

    for file_path in image_files:
        image_id = upload_benchmark_image(
            local_file_path=file_path,
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            image_type=image_type,
        )

        if image_id:
            results["successful"].append(image_id)
        else:
            results["failed"].append(file_path)

    logger.info(
        f"Bulk upload complete. Success: {len(results['successful'])}, Failed: {len(results['failed'])}"
    )

    return results


def verify_image_upload(image_id: UUID) -> bool:
    """
    Verifies that an image was successfully uploaded.

    Args:
        image_id: UUID of the image

    Returns:
        True if image exists and has 'active' status, False otherwise
    """
    image = get_image(image_id)

    if not image:
        logger.error(f"Image {image_id} not found in database")
        return False

    if image.status != ImageStatus.ACTIVE:
        logger.warning(
            f"Image {image_id} has status '{image.status}', expected 'active'"
        )
        return False

    logger.info(f"Image {image_id} verified successfully")
    return True
