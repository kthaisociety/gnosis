from lib.models.vlm import ModelInfo, InferenceConfig
from lib.db import get_all_inference_models


# loads defaults into config without overwriting
def load_defaults(inference_type: str, config: InferenceConfig, defaults: dict):
    # output_schema_name, device_map, use_gpu, api_key
    # have no defaults

    if config.max_tokens is None:
        config.max_tokens = defaults.get("max_tokens")
    if config.temperature is None:
        config.temperature = defaults.get("temperature")
    if config.top_p is None:
        config.top_p = defaults.get("top_p")
    if config.top_k is None:
        config.top_k = defaults.get("top_k")

    if inference_type == "transformers":
        if config.dtype is None:
            config.dtype = defaults.get("dtype")
        if config.model_class is None:
            config.model_class = defaults.get("model_class")
        if config.return_tensors is None:
            config.return_tensors = defaults.get("return_tensors")
        if config.padding is None:
            config.padding = defaults.get("padding")
        if config.attn_implementation is None:
            config.attn_implementation = defaults.get("attn_implementation")


# ensures inference config is valid
# throws error if invalid
# updates inference config with defaults
# returns ModelInfo of model
def validate_config(config: InferenceConfig) -> ModelInfo:
    models = get_all_inference_models()

    # ensure model is supported
    model_info = None
    for model in models:
        if model.model_name == config.model_name:
            model_info = model
            break
    if not model_info:
        raise Exception(f"model {config.model_name} not supported")

    defaults = model_info.default_config
    load_defaults(model_info.inference_type, config, defaults)

    # ensure no gpu mismatch
    if model.requires_gpu and config.use_gpu is False:
        raise Exception(f"model {config.model_name} requires gpu")

    if model_info.inference_type == "api":
        if not config.api_key:
            raise Exception(f"model {config.model_name} requires API key")

    return model_info
