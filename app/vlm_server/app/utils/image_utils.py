from typing import Union, Any
from PIL import Image
from io import BytesIO


def image_from_bytes(data: bytes) -> Image.Image:
    img = Image.open(BytesIO(data))
    # Preserve alpha for palette/transparent images to avoid PIL warning
    if (img.mode == "P" and "transparency" in img.info) or img.mode in ("RGBA", "LA"):
        return img.convert("RGBA")
    return img.convert("RGB")


def normalize_image(image: Union[str, bytes, Image.Image]) -> Any:
    if isinstance(image, bytes):
        return image_from_bytes(image)
    return image


def decode_png_from_bytes(data: bytes) -> Image.Image:
    """Decode arbitrary image bytes and return a PNG-compatible PIL image.
    Ensures output is RGB/RGBA for downstream processing.
    """
    return image_from_bytes(data)
