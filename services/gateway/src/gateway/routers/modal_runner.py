import os
import sys
import time
import asyncio
import types
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import modal

from lib.utils.log import get_logger
from lib.models.vlm import (
    VLMResponseFormat,
    VLMTableOutput,
    DataPoint,
    InferenceConfig,
)

logger = get_logger(__name__)

# Create stub modules for Modal deserialization
# Modal expects these to exist locally to deserialize the remote objects
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
_modal_app_module.VLMOutput = VLMTableOutput
_modal_app_module.DataPoint = DataPoint
_modal_app_module.InferenceConfig = InferenceConfig
sys.modules["modal_app"] = _modal_app_module

# Stub for models.vlm_models (mounted lib path in Modal container)
_models_module = types.ModuleType("models")
_models_vlm_models_module = types.ModuleType("models.vlm_models")
_models_vlm_models_module.VLMOutput = VLMTableOutput
_models_vlm_models_module.DataPoint = DataPoint
_models_vlm_models_module.InferenceConfig = InferenceConfig
sys.modules["models"] = _models_module
sys.modules["models.vlm_models"] = _models_vlm_models_module


from gateway.config import config


def ensure_modal_auth():
    """Ensure Modal credentials are available."""
    if not (config.MODAL_TOKEN_ID and config.MODAL_TOKEN_SECRET):
        raise RuntimeError(
            "Modal credentials not found. Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env"
        )
    # Modal reads credentials from environment variables automatically
    logger.info("Modal credentials found.")


async def run_modal_inference(
    img_bytes: bytes,
    config: InferenceConfig,
) -> VLMResponseFormat:
    try:
        ensure_modal_auth()
        OCRInference = modal.Cls.from_name("gnosis-infer-app", "OCRInference")

        logger.info(f"[ Modal ] Starting inference: model={config.model_name}")

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
        logger.info(f"[ Modal ] done in {processed_time:.1f} ms")

        if isinstance(result, list) and result:
            result = result[0]
        if hasattr(result, "model_dump_json"):
            out = result.model_dump_json(exclude_none=True)
        elif hasattr(result, "model_dump"):
            out = json.dumps(result.model_dump(exclude_none=True))
        elif isinstance(result, dict):
            out = json.dumps(result)
        else:
            out = str(result)
        return VLMResponseFormat(text=out, inference_time_ms=processed_time)

    except Exception as e:
        logger.error(f"[ Modal ] failed inference}: {e}")
        raise
