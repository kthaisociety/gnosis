import cv2
import numpy as np


def decode_image(image_bytes: bytes) -> np.ndarray:
    img = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image bytes")
    return img


def encode_png(image: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Failed to encode image")
    return bytes(buf)
