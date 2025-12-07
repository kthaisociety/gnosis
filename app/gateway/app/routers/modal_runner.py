import os
import sys
import time
import asyncio
import types
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import modal
from app.models.vlm_models import (
    VLMResponseFormat,
    VLMOutput,
    DataPoint,
    InferenceConfig,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Create stub modules for Modal deserialization
_infer_module = types.ModuleType("infer")
_infer_module.vlm = types.ModuleType("infer.vlm")
_infer_module.vlm.vlm = types.ModuleType("infer.vlm.vlm")
_infer_module.vlm.VLMOutput = VLMOutput
_infer_module.vlm.DataPoint = DataPoint
_infer_module.vlm.vlm.VLMOutput = VLMOutput
_infer_module.vlm.vlm.DataPoint = DataPoint
sys.modules["infer"] = _infer_module
sys.modules["infer.vlm"] = _infer_module.vlm
sys.modules["infer.vlm.vlm"] = _infer_module.vlm.vlm


def ensure_modal_auth():
    """Ensure Modal credentials are available."""
    modal_token_id = os.getenv("MODAL_TOKEN_ID")
    modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")

    if not (modal_token_id and modal_token_secret):
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        modal_token_id = os.getenv("MODAL_TOKEN_ID")
        modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")

    if not (modal_token_id and modal_token_secret):
        raise RuntimeError(
            "Modal credentials not found. Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env"
        )

    # Modal reads credentials from environment variables automatically
    logger.info("Modal credentials found.")


async def run_modal_inference(
    img_bytes: bytes,
    config: InferenceConfig,
    prompt: Optional[str],
    filename: str = "",
) -> VLMResponseFormat:
    """Run VLM inference via Modal."""
    try:
        ensure_modal_auth()
        OCRInference = modal.Cls.from_name("gnosis-infer-app", "OCRInference")

        logger.info(f"[Modal] Starting inference: model={config.model_name}")

        t0 = time.perf_counter()
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: OCRInference().infer.remote(
                    [img_bytes],
                    config.model_dump(exclude_none=True),
                    prompt,
                ),
            )

        processed_time = (time.perf_counter() - t0) * 1000
        logger.info(f"[Modal] Done in {processed_time:.1f} ms for {filename}")

        # Normalize result
        if isinstance(result, list) and result:
            first = result[0]
            if hasattr(first, "model_dump_json"):
                json_str = first.model_dump_json(exclude_none=True)
            elif hasattr(first, "model_dump"):
                json_str = json.dumps(first.model_dump(exclude_none=True))
            else:
                return VLMResponseFormat(
                    text=str(first), inference_time_ms=processed_time
                )
        elif isinstance(result, dict):
            json_str = json.dumps(result)
        elif isinstance(result, str):
            try:
                json.loads(result)
                json_str = result
            except:
                return VLMResponseFormat(text=result, inference_time_ms=processed_time)
        else:
            return VLMResponseFormat(text=str(result), inference_time_ms=processed_time)

        return VLMResponseFormat(json_data=json_str, inference_time_ms=processed_time)
    except Exception as e:
        logger.error(f"[Modal] Failed for {filename}: {e}")
        raise
