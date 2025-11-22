from vllm import LLM, SamplingParams
from typing import Any

from .vlm import VLM


class VLMVLLM(VLM):
    def load(self) -> None:
        model_name = self.config.get("model_name")
        dtype = self.config.get("dtype", "bfloat16")
        max_model_len = self.config.get("max_model_len", 8192)

        self.llm = LLM(
            model=model_name,
            trust_remote_code=True,
            download_dir="./weights",
            dtype=dtype,
            max_model_len=max_model_len,
        )

    def run(self, image: Any, prompt: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        sampling_params = SamplingParams(
            temperature=self.config.get("temperature", 0.1),
            max_tokens=self.config.get("max_tokens", 1024),
        )
        if "top_p" in self.config:
            sampling_params.top_p = self.config.get("top_p")
        if "top_k" in self.config:
            sampling_params.top_k = self.config.get("top_k")

        outputs = self.llm.chat([messages], sampling_params=sampling_params)
        return outputs[0].outputs[0].text
