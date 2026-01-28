from typing import Any, List
import os

from lib.models.vlm import InferenceConfig
from lib.utils.log import get_logger
from .vlm import (
    VLM,
    VLMTransformer,
    VLMGemini,
)

logger = get_logger(__name__)


def infer(
    images: List[Any],
    config: InferenceConfig,
    prompt: str = None,
):
    # Ensure model supported and config params match model
    model_info = VLM.get_model_info(config.model_name)
    if not model_info:
        raise ValueError(
            f"model {config.model_name} not supported (supported: {VLM.get_supported_models()}"
        )
    if model_info.requires_gpu is True and not config.use_gpu:
        raise ValueError(f"model {config.model_name} requirest GPU for inference")

    # Set inference class
    if model_info.inference_class == "transformers":
        model = VLMTransformer(config)
    elif model_info.inference_class == "gemini":
        model = VLMGemini(config)
    else:
        raise ValueError(
            f"inference class {model_info.inference_class} not supported (supported: {VLM.get_supported_inference_classes()})"
        )

    # Set prompt
    if not prompt:
        prompt = get_prompt(model_info.default_prompt_name)
        logger.info(
            f"No prompt provided, using default prompt: {prompt[:min(10, len(prompt))]}..."
        )
        if not prompt:
            raise ValueError(
                f"no prompt supplied and no default prompt for {config.model_name}"
            )

    return model.test(images, prompt)


def get_prompt(prompt_name: str):
    try:
        prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
        prompt_paths = os.listdir(prompt_dir)

        for path in prompt_paths:
            if prompt_name == path:
                with open(os.path.join(prompt_dir, path), "r", encoding="UTF-8") as f:
                    return f.read().strip()

    except Exception:
        return None


def download_model(model_name: str):
    if not VLM.is_supported_model(model_name):
        raise ValueError(f"canot download unsupported model {model_name}")

    inference_class = VLM.get_model_inference_class(model_name)
    if inference_class == "transformers":
        try:
            VLMTransformer.download(model_name)
        except Exception as e:
            raise Exception(f"Failed to download transformer {model_name}: {e}")
    else:
        print(f"{model_name} is either an API or has unsupported download")
