from PIL import Image
from openai import OpenAI

from lib.models.vlm import InferenceConfig
from lib.utils.log import get_logger
from lib.utils.image import pil_to_b64
from lib.inference import get_schema

logger = get_logger(__name__)


class GPT:
    def __init__(self, config: InferenceConfig):
        self.config = config
        api_key = (config.api_key or "").strip()
        if not api_key:
            raise ValueError("OpenAI (GPT) requires a non-empty api_key")
        self.client = OpenAI(api_key=api_key)
        self.model = config.model_name

    def _build_input(self, image: Image.Image, prompt: str):
        content = [{"type": "input_text", "text": prompt}]
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{pil_to_b64(image)}",
            }
        )
        return [{"role": "user", "content": content}]

    def run(self, image: Image.Image, prompt: str) -> str:
        prompt = prompt if prompt is not None else ""
        config_kw = {}
        if self.config.temperature is not None:
            config_kw["temperature"] = self.config.temperature
        if self.config.top_p is not None:
            config_kw["top_p"] = self.config.top_p
        if self.config.top_k is not None:
            config_kw["top_k"] = self.config.top_k
        if self.config.max_tokens is not None:
            config_kw["max_output_tokens"] = self.config.max_tokens
        if self.config.system_prompt is not None:
            config_kw["instructions"] = self.config.system_prompt

        input = self._build_input(image, prompt)

        schema = get_schema(self.config.output_schema_name)
        if schema:
            response = self.client.responses.parse(
                model=self.model, input=input, text_format=schema, **config_kw
            )
            result = response.output_parsed
            if result is None:
                return ""
            return result.model_dump_json(exclude_none=True)
        else:
            return self.client.responses.create(
                model=self.model, input=input, **config_kw
            ).output_text
