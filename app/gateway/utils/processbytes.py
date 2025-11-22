import base64
import cv2
import numpy as np


def decode_image_from_base64(image_bytes: bytes) -> np.ndarray:
    """Decode base64-encoded image bytes to numpy array."""
    raw_bytes = base64.b64decode(image_bytes)
    return decode_image_from_bytes(raw_bytes)


def decode_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Decode raw image bytes to numpy array."""
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image bytes")
    return img


def encode_png(image: np.ndarray) -> bytes:
    """Encode numpy array image to PNG bytes."""
    ok, buf = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Failed to encode image")
    return bytes(buf)
