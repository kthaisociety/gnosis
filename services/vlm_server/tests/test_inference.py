from PIL import Image
from dotenv import load_dotenv
import time
import os

from lib.models.vlm import InferenceConfig
from lib.utils.log import get_logger

from vlm_server.inference import inference


logger = get_logger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PROMPT = """
Extract from this graph:
1. Title
2. X-axis label
3. Y-axis label
4. Legend (if present)
5. ALL data values
Required JSON format:
{
    "title": str or null,
    "x_label": str or null,
    "y_label": str or null,
    "legend": ["serie1", "serie2"] or null,
    "data": [{"x": x1, "y": y1}, {"x": x2, "y": y2}, {"x": x3, "y": y3}, ...]
}
Return ONLY the JSON object, nothing else.
"""


def test(image: Image, config: InferenceConfig):
    logger.info("Starting inference...")
    t0 = time.perf_counter()

    try:
        out = inference(image, config)
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return

    logger.info(f"Done in {(time.perf_counter() - t0) * 1000:.1f} ms")
    logger.info(f"Inference output: {out}")


def main():
    assert GEMINI_API_KEY, "env variable GEMINI_API_KEY required"

    # get image
    image_path = os.path.join(os.path.dirname(__file__), "image.png")
    image = Image.open(image_path)
    assert image, f"Could not open image at {image_path}"

    gemini_config = InferenceConfig(
        model_name="gemini-2.5-flash", prompt=PROMPT, api_key=GEMINI_API_KEY
    )
    transformers_config = InferenceConfig(
        model_name="nanonets/Nanonets-OCR2-3B", prompt=PROMPT
    )

    logger.info("Testing gemini inference")
    test(image, gemini_config)

    logger.info("Testing transformers inference")
    test(image, transformers_config)


if __name__ == "__main__":
    main()
