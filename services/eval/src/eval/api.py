from dotenv import load_dotenv
import requests
import os

from lib.models.vlm import InferenceConfig, VLMResponse
from lib.utils.log import get_logger
from lib.utils.image import get_image_mime_type

logger = get_logger(__name__)

load_dotenv()
URL = os.getenv("GATEWAY_URL")


def inference(
    runner: str,
    image_path: str,
    config: InferenceConfig,
) -> VLMResponse:
    try:
        # Get image
        image_res = requests.get(image_path)
        image_res.raise_for_status()
        image_content = image_res.content

        # API request to gateway
        res = requests.post(
            f"{URL}/process",
            data={
                "runner": runner,
                "config": config.model_dump_json(exclude_none=True),
            },
            files={
                "file": (
                    os.path.basename(image_path),
                    image_content,
                    get_image_mime_type(image_path),
                )
            },
        )

        res.raise_for_status()

        return VLMResponse(**res.json())

    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            logger.error(
                f"HTTP Error {e.response.status_code}: {
                         e.response.text}"
            )
        else:
            logger.error(f"HTTP Error: {e}")
        return None

    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return None
