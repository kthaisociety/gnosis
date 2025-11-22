from typing import List, Any
from .prompts import get_prompt
from .vlm import (
    VLM,
    VLMTransformer,
    # VLMVLLM,
    VLMGemini,
    InferenceConfig,
)


def infer(
    images: List[Any],
    config: InferenceConfig,
    prompt: str = None,
):
    model_info = VLM.get_model_info(config.model_name)

    # Ensure model supported and config params match model
    if not model_info:
        supported_models = VLM.get_supported_models()
        raise ValueError(
            f"model {config.model_name} not supported (supported: {supported_models}"
        )
    if not config.use_gpu and model_info.requires_gpu == True:
        raise ValueError(f"model {config.model_name} requirest GPU for inference")

    # Set inference class
    if model_info.inference_class == "transformers":
        model = VLMTransformer(config)
    #   elif model_info.inference_class == "vllm":
    #       model = VLMVLLM(config)
    elif model_info.inference_class == "gemini":
        model = VLMGemini(config)
    else:
        supported_inference_classes = VLM.get_supported_inference_classes()
        raise ValueError(
            f"inference class {model_info.inference_class} not supported (supported: {supported_inference_classes})"
        )

    # Set prompt
    if not prompt:
        default_prompt_name = model_info.default_prompt_name
        if default_prompt_name:
            prompt = get_prompt(default_prompt_name)
        else:
            raise ValueError(
                f"no prompt supplied and no default prompt for {config.model_name}"
            )

    return model.test(images, prompt)


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
