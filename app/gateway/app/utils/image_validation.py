import os
from dataclasses import dataclass
from typing import Optional
from io import BytesIO
from fastapi import UploadFile
from PIL import Image

# Validation config
ALLOWED_MIME_TYPES = os.getenv("ALLOWED_MIME_TYPES", "image/jpeg,image/png").split(",")
MAX_IMAGE_SIZE_BYTES = int(os.getenv("MAX_IMAGE_SIZE_BYTES", "20971520"))  # 20 MiB


@dataclass
class ImageValidationError:
    status: int
    error: str
    message: str


def verify_image_integrity(
    file: UploadFile, image_bytes: bytes, max_byte_size: int = MAX_IMAGE_SIZE_BYTES
) -> Optional[ImageValidationError]:
    """
    Verify that a file is a genuine, unspoofed image.
    Returns None if valid, otherwise return an error.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        return ImageValidationError(
            status=415,  # Unsupported Media Type
            error="unsupported_file_type",
            message=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}.",
        )

    if len(image_bytes) == 0:
        return ImageValidationError(
            status=400,  # Bad Request
            error="empty_image",
            message="Image file is empty.",
        )

    if len(image_bytes) > max_byte_size:
        return ImageValidationError(
            status=413,  # Payload Too Large
            error="image_too_large",
            message=f"Image size {len(image_bytes)} bytes exceeds maximum allowed size of {max_byte_size} bytes.",
        )

    try:
        Image.open(BytesIO(image_bytes)).verify()
    except Exception as e:
        return ImageValidationError(
            status=422,  # Unprocessable Entity
            error="corrupted_file",
            message=f"Invalid or corrupted image file: {e}",
        )

    return None
