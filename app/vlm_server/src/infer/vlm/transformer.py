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
            AutoProcessor.from_pretrained(model_name)
            local_dir = snapshot_download(model_name)
        else:
            raise ValueError(
                "cannot download {model_name} to cache since it's an unsupported model"
            )

    def load(self) -> None:
        import torch
        
        model_name = self.config.get("model_name")
        model_class = self.config.get("model_class")
        use_gpu = self.config.get("use_gpu", True)
        dtype_str = self.config.get("dtype", "auto")
        device_map = self.config.get("device_map", "auto")

        # Use attn_implementation from config, or default based on GPU availability
        attn_implementation = self.config.get("attn_implementation")
        if attn_implementation is None:
            attn_implementation = "flash_attention_2" if use_gpu else "sdpa"
        
        # Convert dtype string to torch dtype
        if dtype_str == "auto":
            torch_dtype = None
        elif dtype_str == "bfloat16":
            torch_dtype = torch.bfloat16
        elif dtype_str == "float16":
            torch_dtype = torch.float16
        else:
            torch_dtype = None

        # Set device_map based on GPU availability
        if not use_gpu:
            device_map = "cpu"
        elif device_map == "auto" and use_gpu:
            device_map = "auto"

        # Ensure model class is supported
        if model_class not in MODEL_CLASS:
            raise ValueError(f"unsupported model class {model_class}")
        t0 = time.perf_counter()
        logger.info(f"loading {model_name} class={model_class} use_gpu={use_gpu} device_map={device_map}")
        self.processor = AutoProcessor.from_pretrained(model_name)
        
        # Load model with proper kwargs
        load_kwargs = {
            "attn_implementation": attn_implementation,
        }
        if torch_dtype is not None:
            load_kwargs["torch_dtype"] = torch_dtype
        if device_map:
            load_kwargs["device_map"] = device_map
        
        self.model = MODEL_CLASS[model_class].from_pretrained(
            model_name,
            **load_kwargs
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
