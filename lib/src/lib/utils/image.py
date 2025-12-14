import base64
import io
from typing import Union
import cv2
import numpy as np
from PIL import Image
import os

MAX_SIZE = int(os.getenv("MAX_IMAGE_SIZE_BYTES", "20971520"))  # 20MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_image_bytes(data: bytes) -> None:
    """Validates image size, integrity, and format. Raises ValueError on failure."""
    # 1. Size Check
    if len(data) > MAX_SIZE:
        raise ValueError(f"Image too large ({len(data)} > {MAX_SIZE} bytes)")
    if len(data) == 0:
        raise ValueError("Image file is empty")

    # 2. Integrity & Format
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()  # Check for broken streams
            if img.format.upper() not in ALLOWED_FORMATS:
                raise ValueError(
                    f"Format {img.format} not allowed. Use: {ALLOWED_FORMATS}"
                )
    except Exception as e:
        raise ValueError(f"Corrupted or invalid image: {e}")


def bytes_to_cv2(data: bytes) -> np.ndarray:
    """Decode raw bytes to OpenCV BGR array."""
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode bytes to OpenCV image")
    return img


def b64_to_cv2(data: Union[bytes, str]) -> np.ndarray:
    """Decode base64 (bytes or string) to OpenCV BGR array."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return bytes_to_cv2(base64.b64decode(data))


def cv2_to_bytes(img: np.ndarray, fmt: str = ".png") -> bytes:
    """Encode OpenCV array to raw bytes."""
    ok, buf = cv2.imencode(fmt, img)
    if not ok:
        raise RuntimeError("Failed to encode image")
    return bytes(buf)


def bytes_to_pil(data: bytes) -> Image.Image:
    """Decode raw bytes to PIL Image (RGB)."""
    img = Image.open(io.BytesIO(data))
    # Handle transparency/palettes to avoid errors later
    if img.mode == "P" and "transparency" in img.info:
        return img.convert("RGBA")
    return img.convert("RGB")


def ensure_pil(data: Union[bytes, Image.Image]) -> Image.Image:
    """
    Ensure input is a PIL Image.
    If bytes are provided, decode them. If it's already an Image, return it.
    """
    if isinstance(data, bytes):
        return bytes_to_pil(data)
    return data
