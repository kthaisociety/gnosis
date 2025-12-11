import os
from dataclasses import dataclass
from typing import Optional
from io import BytesIO
from fastapi import UploadFile
from PIL import Image

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}  # PIL format names are uppercase
MAX_SIZE = int(os.getenv("MAX_IMAGE_SIZE_BYTES", "20971520"))  # 20 MB


@dataclass
class ImageValidationError:
    status: int
    error: str
    message: str


def verify_image_integrity(
    file: UploadFile, image_bytes: bytes
) -> Optional[ImageValidationError]:

    # 1. Fast Size Check
    if len(image_bytes) > MAX_SIZE:
        return ImageValidationError(413, "image_too_large", f"Image exceeds {MAX_SIZE} bytes.")

    if len(image_bytes) == 0:
        return ImageValidationError(400, "empty_image", "File is empty.")

    # 2. Integrity & Format Check (Trust the bytes, not the header)
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            img.verify()  # Checks for broken data streams

            if img.format.upper() not in ALLOWED_FORMATS:
                return ImageValidationError(
                    415,
                    "unsupported_type",
                    f"Detected format {img.format} not allowed. Use: {
                        ALLOWED_FORMATS}"
                )

    except Exception as e:
        return ImageValidationError(422, "corrupted", f"Cannot parse image: {str(e)}")

    return None
