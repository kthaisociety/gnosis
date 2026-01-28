from typing import Any
from google import genai
from google.genai import types

from .vlm import VLM


class VLMGemini(VLM):
    def load(self) -> None:
        self.client = genai.Client(api_key=self.config.get("api_key"))
        self.model = self.config.get("model_name")

    def run(self, image: Any, prompt: str) -> str:
        temperature = self.config.get("temperature", 0.1)
        top_p = self.config.get("top_p", 0.9)
        top_k = self.config.get("top_k", 40)
        max_output_tokens = self.config.get("max_tokens", 8192)
        output_schema = self.config.get("output_schema", None)

        if not output_schema:
            raise ValueError("No output schema found for inference!")

        response = self.client.models.generate_content(
            model=self.model,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=max_output_tokens,
                response_mime_type="application/json",
                response_schema=output_schema,
            ),
        )

        return response.text

    @classmethod
    def download(cls, model_name) -> None:
        return
