from PIL import Image
from google import genai
from google.genai import types

from lib.models.vlm import InferenceConfig
from lib.utils.log import get_logger
from lib.inference import get_schema

logger = get_logger(__name__)


class Gemini:
    def __init__(self, config: InferenceConfig):
        self.config = config
        api_key = (config.api_key or "").strip()
        if not api_key:
            raise ValueError("Gemini requires a non-empty api_key")
        self.client = genai.Client(api_key=api_key)
        self.model = config.model_name

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
            config_kw["system_instruction"] = self.config.system_prompt

        schema = get_schema(self.config.output_schema_name)
        if schema:
            config_kw["response_mime_type"] = "application/json"
            config_kw["response_schema"] = schema

        response = self.client.models.generate_content(
            model=self.model,
            contents=[image, prompt],
            config=types.GenerateContentConfig(**config_kw) if config_kw else None,
        )

        if not response or not getattr(response, "text", None):
            return ""
        return response.text
