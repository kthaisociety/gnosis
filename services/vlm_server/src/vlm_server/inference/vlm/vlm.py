from abc import ABC, abstractmethod
from typing import Any, Optional, List, Type, TypeVar
import json
import re
import os

from lib.models import (
    ModelInfo,
    InferenceConfig
)


# For generic structured output schemas
T = TypeVar("T")


# Main VLM Abstract class
# Inherit from when implementing inference for a new model/model type
class VLM(ABC):
    model_info = {}
    model_info_loaded = False

    def __init__(self, config: InferenceConfig):
        self.config = self.get_config(config)
        self.loaded = False

    def get_config(self, config: InferenceConfig):
        ret = VLM.model_info[config.model_name].default_config.copy()
        ret.update(config.model_dump(exclude_none=True))
        ret["output_schema"] = VLM.get_output_schema(config.output_schema_name)
        return ret

    @classmethod
    def get_output_schema(cls, name: str | None):
        if not name:
            raise ValueError("No output schema name supplied")

        from lib.models import VLMTableOutput
        if name == "VLMTableOutput":
            return VLMTableOutput
        else:
            raise ValueError(f"Unknown schema: {name}")

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
            print(
                f"model '{model_name}' not found in models.json (unsupported)")
            return None

        return cls.model_info[model_name]

    @classmethod
    def get_supported_inference_classes(cls):
        if not cls.model_info_loaded:
            cls.load_model_info()

        supported_inference_classes = []
        for key in cls.model_info:
            supported_inference_classes.append(
                cls.model_info[key].inference_class)
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

    def parse_output(self, text: str, schema: Type[T]) -> Optional[T]:
        try:
            # Strip markdown code blocks (```json ... ``` or ``` ... ```)
            text = re.sub(r"^```(?:json)?\s*", "",
                          text.strip(), flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            json_str = json_match.group() if json_match else text
            parsed_json = json.loads(json_str)
            return schema(**parsed_json)
        except (json.JSONDecodeError, Exception) as e:
            print(f"parse error to {schema.__name__}: {e} ({text})")
            return None

    def test(self, images: List[Any], prompt: str) -> Optional[List[T]]:
        if not self.loaded:
            try:
                self.load()
                self.loaded = True
            except Exception as e:
                raise Exception(
                    f"Failed to load model of inference class {
                        self.config.get(
                            'inference_class', '<could not get inference class>'
                        )
                    }: {e}"
                )

        try:
            ret = []
            for image in images:
                raw_output = self.run(image, prompt)
                ret.append(self.parse_output(
                    raw_output, self.config.get("output_schema")))
        except Exception as e:
            raise Exception(
                f"Failed to inference model of inference class {
                    self.config.get(
                        'inference_Class', '<could not get inference class>'
                    )
                }: {e}"
            )

        return ret
