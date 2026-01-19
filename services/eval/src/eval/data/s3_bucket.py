import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from typing import Optional, Tuple
from uuid import UUID, uuid4
import os
import mimetypes

from lib.utils.log import get_logger

load_dotenv()
logger = get_logger(__name__)

# Environment variables
S3_BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_ENDPOINT_URL = os.getenv("ENDPOINT_URL")
S3_ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

# S3 client configuration for Cloudflare R2
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY_ID,
    aws_secret_access_key=S3_SECRET_ACCESS_KEY,
    region_name="auto",
)


def ensure_s3_bucket_exists() -> bool:
    """
    Ensures the S3 bucket exists, creates it if it doesn't.

    Returns:
        bool: True if bucket exists or was created successfully
    """
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"S3 bucket '{S3_BUCKET_NAME}' exists")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            try:
                logger.info(f"Creating S3 bucket '{S3_BUCKET_NAME}'...")
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                logger.info(f"S3 bucket '{S3_BUCKET_NAME}' created successfully")
                return True
            except Exception as create_error:
                logger.error(f"Failed to create S3 bucket: {create_error}")
                return False
        else:
            logger.error(f"Error checking bucket: {e}")
            return False


def generate_s3_key(
    dataset_name: str, file_extension: str, image_uuid: Optional[UUID] = None
) -> Tuple[UUID, str]:
    """
    Generates a UUID-based S3 key for an image.

    Args:
        dataset_name: Name of the dataset
        file_extension: File extension (e.g., 'png', 'jpg')
        image_uuid: Optional existing UUID, generates new one if not provided

    Returns:
        Tuple of (UUID, s3_key)
        Example: (UUID('...'), 'datasets/my_dataset/550e8400-e29b-41d4-a716-446655440000.png')
    """
    if image_uuid is None:
        image_uuid = uuid4()

    # Ensure extension doesn't have a leading dot
    extension = file_extension.lstrip(".")

    # S3 key format: datasets/{dataset_name}/{uuid}.{extension}
    s3_key = f"datasets/{dataset_name}/{image_uuid}.{extension}"

    return image_uuid, s3_key


def upload_image_to_s3(
    local_file_path: str, s3_key: str, content_type: Optional[str] = None
) -> Optional[str]:
    """
    Uploads an image file to S3.

    Args:
        local_file_path: Path to local image file
        s3_key: S3 key/path where file will be stored
        content_type: MIME type (auto-detected if not provided)

    Returns:
        ETag of uploaded file, or None if upload failed
    """
    try:
        # Auto-detect content type if not provided
        if content_type is None:
            content_type, _ = mimetypes.guess_type(local_file_path)
            if content_type is None:
                content_type = "application/octet-stream"

        # Get file size
        file_size = os.path.getsize(local_file_path)

        logger.info(
            f"Uploading {local_file_path} ({file_size} bytes) to s3://{S3_BUCKET_NAME}/{s3_key}"
        )

        with open(local_file_path, "rb") as f:
            response = s3_client.put_object(
                Bucket=S3_BUCKET_NAME, Key=s3_key, Body=f, ContentType=content_type
            )

        etag = response.get("ETag", "").strip('"')
        logger.info(f"Upload successful. ETag: {etag}")
        return etag

    except Exception as e:
        logger.error(f"Failed to upload {local_file_path} to S3: {e}")
        return None


def get_image_metadata(local_file_path: str) -> dict:
    """
    Extracts metadata from a local image file.

    Args:
        local_file_path: Path to local image file

    Returns:
        Dictionary with width, height, format, file_size_bytes
    """
    from PIL import Image

    metadata = {"width": None, "height": None, "format": None, "file_size_bytes": None}

    try:
        # Get file size
        metadata["file_size_bytes"] = os.path.getsize(local_file_path)

        # Get image dimensions and format
        with Image.open(local_file_path) as img:
            metadata["width"] = img.width
            metadata["height"] = img.height
            metadata["format"] = img.format.lower() if img.format else None

    except Exception as e:
        logger.warning(f"Could not extract image metadata from {local_file_path}: {e}")

    return metadata


def delete_image_from_s3(s3_key: str) -> bool:
    """
    Deletes an image from S3.

    Args:
        s3_key: S3 key/path of the file to delete

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        logger.info(f"Deleting s3://{S3_BUCKET_NAME}/{s3_key}")
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        logger.info(f"Successfully deleted {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete {s3_key} from S3: {e}")
        return False


def delete_dataset_images(dataset_name: str) -> bool:
    """
    Deletes all images in a dataset from S3.

    Args:
        dataset_name: Name of the dataset

    Returns:
        True if all deletions were successful, False otherwise
    """
    try:
        prefix = f"datasets/{dataset_name}/"
        logger.info(f"Deleting all objects with prefix: {prefix}")

        # List all objects with the prefix
        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix)

        deleted_count = 0
        for page in pages:
            if "Contents" not in page:
                continue

            # Delete objects in batches
            objects_to_delete = [{"Key": obj["Key"]} for obj in page["Contents"]]

            if objects_to_delete:
                s3_client.delete_objects(
                    Bucket=S3_BUCKET_NAME, Delete={"Objects": objects_to_delete}
                )
                deleted_count += len(objects_to_delete)

        logger.info(f"Deleted {deleted_count} objects from dataset '{dataset_name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to delete dataset images for '{dataset_name}': {e}")
        return False


def get_s3_url(s3_key: str, signed: bool = True, expiration: int = 3600) -> str:
    """
    Generates a URL for an S3 object.

    Args:
        s3_key: S3 key/path of the object
        signed: If True, returns pre-signed URL (default). If False, returns public URL.
        expiration: Expiration time in seconds for signed URLs (default 1 hour)

    Returns:
        URL for the object
    """
    if signed:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expiration,
        )
    return f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/{s3_key}"


def check_image_exists(s3_key: str) -> bool:
    """
    Checks if an image exists in S3.

    Args:
        s3_key: S3 key/path to check

    Returns:
        True if object exists, False otherwise
    """
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            logger.error(f"Error checking if {s3_key} exists: {e}")
            return False


if __name__ == "__main__":
    # Test bucket creation
    ensure_s3_bucket_exists()
