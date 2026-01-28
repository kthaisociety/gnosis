from PIL import Image
from google import genai
from google.genai import types

from lib.models.vlm import InferenceConfig
from lib.inference import get_output_schema


class Gemini:
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.client = genai.Client(api_key=self.config.api_key)
        self.model = self.config.model_name

    def run(self, image: Image, prompt: str) -> str:
        temp = self.config.temperature
        top_p = self.config.top_p
        top_k = self.config.top_k
        max_tokens = self.config_max_tokens

        schema = get_output_schema(self.config.output_schema)
        if not schema:
            pass  # TODO

        response = self.client.models.generate_content(
            model=self.model,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                temperature=temp,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=schema
            )
        )

        return response.text
