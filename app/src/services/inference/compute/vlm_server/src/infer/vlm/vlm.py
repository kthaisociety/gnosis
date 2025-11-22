from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import json
import re
import os


class DataPoint(BaseModel):
    x: float
    y: float


class VLMOutput(BaseModel):
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    legend: Optional[List[str]] = None
    data: List[DataPoint]


class ModelInfo(BaseModel):
    model_name: str
    inference_type: str
    inference_class: str
    requires_gpu: Optional[bool] = True
    default_prompt_name: Optional[str] = None
    default_config: Optional[Dict[str, Any]] = {}


class InferenceConfig(BaseModel):
    model_name: str
    use_gpu: Optional[bool] = None

    # Common parameters
    dtype: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[float] = None

    # API models
    api_key: Optional[str] = None

    # vLLM models
    max_model_len: Optional[int] = None

    # Transformers models
    model_class: Optional[str] = None
    device_map: Optional[str] = None
    return_tensors: Optional[str] = None
    padding: Optional[str] = None
    attn_implementation: Optional[str] = None  # "eager", "sdpa", "flash_attention_2"


# Main VLM Abstract class
# Inherit from when implementing inference for a new model/model type
class VLM(ABC):
    model_info = {}
    model_info_loaded = False

    def __init__(self, config: InferenceConfig):
        self.config = self.get_config(config)
        self.loaded = False

    def get_config(self, config: InferenceConfig):
        default_config = VLM.model_info[config.model_name].default_config.copy()
        config_dict = config.model_dump(exclude_none=True)
        default_config.update(config_dict)
        return default_config

    @classmethod
    def load_model_info(cls, path: str = None):
        try:
            if not path:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(current_dir, "models.json")

            with open(path, "r", encoding="UTF-8") as f:
                data = json.load(f)

            cls.model_info = {}
            for model_name, model_data in data.items():
                model_data["model_name"] = model_name
                cls.model_info[model_name] = ModelInfo(**model_data)

            cls.model_info_loaded = True

        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"could not parse {path} for model info: {e}")

    @classmethod
    def get_model_info(cls, model_name: str):
        if not cls.model_info_loaded:
            cls.load_model_info()

        if model_name not in cls.model_info:
            print(f"model '{model_name}' not found in models.json (unsupported)")
            return None

        return cls.model_info[model_name]

    @classmethod
    def get_supported_inference_classes(cls):
        if not cls.model_info_loaded:
            cls.load_model_info()

        supported_inference_classes = []
        for key in cls.model_info:
            supported_inference_classes.append(cls.model_info[key].inference_class)
        return supported_inference_classes

    @classmethod
    def get_supported_models(cls):
        if not cls.model_info_loaded:
            cls.load_model_info()

        supported_models = []
        for model in cls.model_info:
            supported_models.append(model)
        return supported_models

    @classmethod
    def is_supported_model(cls, model_name: str) -> bool:
        supported_models = cls.get_supported_models()
        if model_name in supported_models:
            return True
        return False

    @classmethod
    def get_model_inference_class(cls, model_name: str) -> str:
        if cls.is_supported_model(model_name):
            return cls.model_info[model_name].inference_class
        else:
            raise ValueError(
                f"cannot get inference class of unsupported model {model_name}"
            )

    @abstractmethod
    def download(cls, model_name: str) -> None:
        pass

    @abstractmethod
    def load(self) -> None:
        pass

    @abstractmethod
    def run(self, image: Any, prompt: str) -> str:
        pass

    def parse_output(self, text: str) -> Optional[VLMOutput]:
        try:
            # Strip markdown code blocks (```json ... ``` or ``` ... ```)
            text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            json_str = json_match.group() if json_match else text
            parsed_json = json.loads(json_str)
            return VLMOutput(**parsed_json)
        except (json.JSONDecodeError, Exception) as e:
            print(f"parse error to VLMOutput: {e} ({text})")
            return None

    def test(self, images: List[Any], prompt: str) -> Optional[VLMOutput]:
        if not self.loaded:
            self.load()
            self.loaded = True

        ret = []
        for image in images:
            raw_output = self.run(image, prompt)
            ret.append(self.parse_output(raw_output))

        return ret
