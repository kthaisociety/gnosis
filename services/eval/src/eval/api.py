from dotenv import load_dotenv
import requests
import json
import os

from lib.models.vlm_models import InferenceConfig, VLMResponseFormat
from lib.utils.log import get_logger
from lib.utils.image import get_image_mime_type

logger = get_logger(__name__)

load_dotenv()
URL = os.getenv("GATEWAY_URL")


def infer(
    runner: str,
    image_path: str,
    prompt: str,
    config: InferenceConfig,
    local_imgs: bool = True,
):
    if not local_imgs:
        raise ValueError("Inference with non-local images is unsupported.")

    try:
        with open(image_path, "rb") as f:
            res = requests.post(
                f"{URL}/process",
                data={
                    "runner": runner,
                    "config": json.dumps(config.model_dump()),
                    "prompt": prompt,
                },
                files={
                    "file": (
                        os.path.basename(image_path),
                        f,
                        get_image_mime_type(image_path),
                    )
                },
            )

            res.raise_for_status()

            return VLMResponseFormat(**res.json())

    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
        else:
            logger.error(f"HTTP Error: {e}")
        return None

    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return None
