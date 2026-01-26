import os
import sys
import time
import asyncio
import types
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import modal
from lib.models.vlm_models import (
    VLMResponseFormat,
    VLMTableOutput,
    DataPoint,
    InferenceConfig,
)
from lib.utils.log import get_logger

logger = get_logger(__name__)

# Create stub modules for Modal deserialization
_infer_module = types.ModuleType("infer")
_infer_module.vlm = types.ModuleType("infer.vlm")
_infer_module.vlm.vlm = types.ModuleType("infer.vlm.vlm")
_infer_module.vlm.DataPoint = DataPoint
_infer_module.vlm.VLMTableOutput = VLMTableOutput
_infer_module.vlm.vlm.DataPoint = DataPoint
_infer_module.vlm.vlm.VLMTableOutput = VLMTableOutput
sys.modules["infer"] = _infer_module
sys.modules["infer.vlm"] = _infer_module.vlm
sys.modules["infer.vlm.vlm"] = _infer_module.vlm.vlm

# Stub for modal_app module (where VLMOutput is defined in the Modal deployment)
_modal_app_module = types.ModuleType("modal_app")
_modal_app_module.VLMOutput = VLMOutput
_modal_app_module.DataPoint = DataPoint
_modal_app_module.InferenceConfig = InferenceConfig
sys.modules["modal_app"] = _modal_app_module

# Stub for models.vlm_models (mounted lib path in Modal container)
_models_module = types.ModuleType("models")
_models_vlm_models_module = types.ModuleType("models.vlm_models")
_models_vlm_models_module.VLMOutput = VLMOutput
_models_vlm_models_module.DataPoint = DataPoint
_models_vlm_models_module.InferenceConfig = InferenceConfig
sys.modules["models"] = _models_module
sys.modules["models.vlm_models"] = _models_vlm_models_module


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
        json_data: Optional[str] = None
        text_data: Optional[str] = None

        if isinstance(result, list) and result:
            result = result[0]

        if hasattr(result, "model_dump_json"):
            json_data = result.model_dump_json(exclude_none=True)
        elif hasattr(result, "model_dump"):
            json_data = json.dumps(result.model_dump(exclude_none=True))
        elif isinstance(result, dict):
            json_data = json.dumps(result)
        elif isinstance(result, str):
            try:
                json.loads(result)
                json_data = result
            except json.JSONDecodeError:
                text_data = result
        else:
            text_data = str(result)

        if json_data:
            return VLMResponseFormat(
                json_data=json_data, inference_time_ms=processed_time
            )
        else:
            return VLMResponseFormat(text=text_data, inference_time_ms=processed_time)

    except Exception as e:
        logger.error(f"[Modal] Failed for {filename}: {e}")
        raise
