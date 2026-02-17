from PIL import Image

from lib.utils.log import get_logger
from lib.models.vlm import ModelInfo, InferenceConfig
from lib.inference import validate_config

from .transformer import Transformer
from .gemini import Gemini
from .gpt import GPT

logger = get_logger(__name__)


def make_model(model_info: ModelInfo, config: InferenceConfig):
    inference_class = model_info.inference_class
    if inference_class == "transformers":
        return Transformer(config)
    elif inference_class == "gemini":
        return Gemini(config)
    elif inference_class == "gpt":
        return GPT(config)
    else:
        raise Exception(f"inference class '{inference_class}' is not supported")


def inference(image: Image.Image, config: InferenceConfig) -> str:
    model_info = validate_config(config)
    model = make_model(model_info, config)
    return model.run(image, config.prompt)
