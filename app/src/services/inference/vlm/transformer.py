from typing import Any
import time
from huggingface_hub import snapshot_download
from transformers import (
    AutoProcessor,
    AutoModelForImageTextToText,
)

from .vlm import VLM
from utils.logging import get_logger

MODEL_CLASS = {"AutoModelForImageTextToText": AutoModelForImageTextToText}

logger = get_logger(__name__)


# Inference transformer type models
class VLMTransformer(VLM):
    @classmethod
    def download(cls, model_name) -> None:
        if cls.is_supported_model(model_name):
            try:
                AutoProcessor.from_pretrained(model_name)
                local_dir = snapshot_download(model_name)
            except ValueError as e:
                raise ValueError(
                    f"Failed to download transformer model {model_name}: {e}"
                )
        else:
            raise ValueError(
                "cannot download {model_name} to cache since it's an unsupported model"
            )

    def load(self) -> None:
        model_name = self.config.get("model_name")
        model_class = self.config.get("model_class")
        use_gpu = self.config.get("use_gpu", True)
        dtype = self.config.get("dtype", "auto")
        device_map = self.config.get("device_map", "auto")

        # Use attn_implementation from config, or default based on GPU availability
        attn_implementation = self.config.get("attn_implementation")
        if attn_implementation is None:
            attn_implementation = "flash_attention_2" if use_gpu else "sdpa"
        device_map = device_map if use_gpu else "cpu"

        # Ensure model class is supported
        if model_class not in MODEL_CLASS:
            raise ValueError(f"unsupported model class {model_class}")
        t0 = time.perf_counter()
        logger.info(f"loading {model_name} class={model_class} use_gpu={use_gpu}")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = MODEL_CLASS[model_class].from_pretrained(
            model_name,
            dtype=dtype,
            device_map=device_map,
            attn_implementation=attn_implementation,
        )
        logger.info(f"loaded {model_name} in {time.perf_counter() - t0:.2f}s")

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

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        return_tensors = self.config.get("return_tensors", "pt")
        padding = self.config.get("padding", True)

        inputs = self.processor(
            text=[text], images=[image], padding=padding, return_tensors=return_tensors
        ).to(self.model.device)

        max_tokens = self.config.get("max_tokens", 8192)
        logger.debug(f"generate start max_tokens={max_tokens}")
        t0 = time.perf_counter()
        generated_ids = self.model.generate(**inputs, max_new_tokens=max_tokens)
        logger.info(f"generate done in {time.perf_counter() - t0:.2f}s")

        if not self.model.config.is_encoder_decoder:
            generated_ids = [
                out_ids[len(in_ids) :]
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]

        return self.processor.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
