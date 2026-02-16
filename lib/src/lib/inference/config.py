from lib.models.vlm import ModelInfo, InferenceConfig
from lib.db import get_all_inference_models

SUPPORTED_TRANSFORMER_MODEL_CLASSES = frozenset({"AutoModelForImageTextToText"})


# load defaults into config without overwriting
def load_defaults(inference_type: str, config: InferenceConfig, defaults: dict) -> None:
    if not isinstance(defaults, dict):
        return
    for key in ("max_tokens", "temperature", "top_p", "top_k"):
        if key not in defaults or defaults[key] is None:
            continue
        if getattr(config, key) is None:
            setattr(config, key, defaults[key])
    if inference_type == "transformers":
        for key in (
            "dtype",
            "model_class",
            "return_tensors",
            "padding",
            "attn_implementation",
        ):
            if key not in defaults or defaults[key] is None:
                continue
            if getattr(config, key) is None:
                setattr(config, key, defaults[key])


def _validate_gemini(config: InferenceConfig, model_name: str) -> None:
    if not (config.api_key or "").strip():
        raise ValueError(f"model '{model_name}' requires a non-empty api_key")
    if config.temperature is not None and not (0 <= config.temperature <= 2):
        raise ValueError(
            f"model '{model_name}': temperature must be in [0, 2], got {config.temperature}"
        )
    if config.top_p is not None and not (0 < config.top_p <= 1):
        raise ValueError(
            f"model '{model_name}': top_p must be in (0, 1], got {config.top_p}"
        )
    if config.top_k is not None and (
        not isinstance(config.top_k, int) or config.top_k < 1
    ):
        raise ValueError(
            f"model '{model_name}': top_k must be a positive int, got {config.top_k}"
        )
    if config.max_tokens is not None and (
        not isinstance(config.max_tokens, int) or config.max_tokens < 1
    ):
        raise ValueError(
            f"model '{model_name}': max_tokens must be a positive int, got {config.max_tokens}"
        )


def _validate_transformers(config: InferenceConfig, model_name: str) -> None:
    if config.model_class is None:
        raise ValueError(f"model '{model_name}' requires model_class")
    if config.model_class not in SUPPORTED_TRANSFORMER_MODEL_CLASSES:
        raise ValueError(
            f"model '{model_name}': unsupported model_class '{config.model_class}' "
            f"(supported: {sorted(SUPPORTED_TRANSFORMER_MODEL_CLASSES)})"
        )
    if config.use_gpu is False and config.attn_implementation == "flash_attention_2":
        raise ValueError(
            f"model '{model_name}': flash_attention_2 requires use_gpu=True"
        )
    if config.max_tokens is None:
        raise ValueError(f"model '{model_name}' (transformers) requires max_tokens")
    if not isinstance(config.max_tokens, int) or config.max_tokens < 1:
        raise ValueError(
            f"model '{model_name}': max_tokens must be a positive int, got {config.max_tokens}"
        )


# Validate config, apply defaults, return ModelInfo for the model.
def validate_config(config: InferenceConfig) -> ModelInfo:
    models = get_all_inference_models()
    model_info = None
    for m in models:
        if m.model_name == config.model_name:
            model_info = m
            break
    if not model_info:
        raise ValueError(f"model '{config.model_name}' is not supported")

    defaults = (
        model_info.default_config if model_info.default_config is not None else {}
    )
    load_defaults(model_info.inference_type, config, defaults)

    if getattr(model_info, "requires_gpu", True) and config.use_gpu is False:
        raise ValueError(f"model '{config.model_name}' requires GPU (use_gpu=True)")

    if model_info.inference_type == "api":
        _validate_gemini(config, config.model_name)
    elif model_info.inference_type == "transformers":
        _validate_transformers(config, config.model_name)

    return model_info
