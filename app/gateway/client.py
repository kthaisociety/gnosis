import os
import sys
import time
import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor

import modal
from app.models.vlm_models import VLMResponseFormat
from app.utils.logging import get_logger

logger = get_logger(__name__)


def ensure_modal_auth():
    """Ensure Modal credentials are available. Modal reads from environment variables automatically."""
    modal_token_id = os.getenv("MODAL_TOKEN_ID")
    modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")

    if not (modal_token_id and modal_token_secret):
        # Try loading from .env file
        try:
            from dotenv import load_dotenv

            load_dotenv()
            modal_token_id = os.getenv("MODAL_TOKEN_ID")
            modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")
        except ImportError:
            pass

    if not (modal_token_id and modal_token_secret):
        raise ValueError(
            "Modal credentials not found. Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env"
        )

    logger.info("Modal credentials found.")


async def query_vlm(img_bytes: bytes, filename: str = "") -> VLMResponseFormat:
    """Query VLM via Modal inference."""
    try:
        ensure_modal_auth()

        # Look up the deployed OCRInference class
        OCRInference = modal.Cls.from_name("gnosis-infer-app", "OCRInference")

        # Configure inference
        infer_config = {
            "model_name": "nanonets/Nanonets-OCR-s",
            "use_gpu": True,
            "attn_implementation": "sdpa",
        }

        # Get prompt (default) - try to import, fallback to None if not available
        try:
            import sys

            vlm_server_path = os.path.join(
                os.path.dirname(__file__),
                "services",
                "inference",
                "compute",
                "vlm_server",
                "src",
            )
            if vlm_server_path not in sys.path:
                sys.path.insert(0, vlm_server_path)
            from infer.prompts import get_prompt

            prompt = get_prompt("default")
        except Exception:
            prompt = None
            logger.warning("Could not load default prompt, using None")

        t0 = time.perf_counter()
        # Call Modal inference (run in executor since .remote() is blocking)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: OCRInference().infer.remote([img_bytes], infer_config, prompt),
            )
        t1 = time.perf_counter()
        processed_time = (t1 - t0) * 1000

        logger.info(
            f"[Modal] Inference finished in {processed_time:.1f} ms for {filename}"
        )

        # Extract result - Modal returns a list of VLMOutput objects
        if isinstance(result, list) and result:
            first = result[0]
            if hasattr(first, "model_dump_json"):
                json_str = first.model_dump_json(exclude_none=True)
            elif hasattr(first, "json"):
                json_str = first.json
            else:
                json_str = str(first)

            return VLMResponseFormat(json=json_str, inference_time_ms=processed_time)
        else:
            return VLMResponseFormat(text=str(result), inference_time_ms=processed_time)
    except Exception as e:
        logger.error(f"[Modal] Failed to query VLM for {filename}: {e}")
        raise


if __name__ == "__main__":
    logger.info("gRPC client module loaded")
