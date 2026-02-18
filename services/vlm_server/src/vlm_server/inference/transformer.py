import time
from PIL import Image
import torch
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
    GenerationConfig,
)

from lib.models.vlm import InferenceConfig
from lib.utils.log import get_logger

logger = get_logger(__name__)

MODEL_CLASS = {"AutoModelForImageTextToText": AutoModelForImageTextToText}


def _device_map(use_gpu: bool | None, explicit: str | None) -> str:
    if use_gpu is False:
        return "cpu"
    if explicit is not None:
        return explicit
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class Transformer:
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.load_model()

    def load_model(self):
        model_name = self.config.model_name
        model_class = self.config.model_class
        use_gpu = self.config.use_gpu
        dtype = self.config.dtype or "auto"
        device_map = _device_map(use_gpu, self.config.device_map)
        attn_implementation = self.config.attn_implementation
        if attn_implementation is None:
            attn_implementation = "flash_attention_2" if use_gpu else "sdpa"
        if attn_implementation == "flash_attention_2" and not use_gpu:
            logger.warning("flash_attention_2 requires gpu, defaulting to sdpa")
            attn_implementation = "sdpa"

        if model_class not in MODEL_CLASS:
            raise ValueError(
                f"unsupported model_class '{model_class}' (supported: {list(MODEL_CLASS)})"
            )

        logger.info(f"loading {model_name}... (device={device_map})")
        t0 = time.perf_counter()

        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = MODEL_CLASS[model_class].from_pretrained(
            model_name,
            dtype=dtype,
            device_map=device_map,
            attn_implementation=attn_implementation,
            low_cpu_mem_usage=False,
        )

        logger.info(
            f"loaded {model_name} in {(time.perf_counter() - t0) * 1000:.0f} ms"
        )

    def run(self, image: Image.Image, prompt: str) -> str:
        prompt = prompt if prompt is not None else ""
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

        padding = True if self.config.padding is None else self.config.padding
        return_tensors = self.config.return_tensors or "pt"
        inputs = self.processor(
            text=[text],
            images=[image],
            padding=padding,
            return_tensors=return_tensors,
        ).to(self.model.device)

        logger.info("generating...")
        t0 = time.perf_counter()

        gen_config = GenerationConfig(
            max_new_tokens=self.config.max_tokens,
            do_sample=False,
        )
        generated_ids = self.model.generate(**inputs, generation_config=gen_config)

        logger.info(f"generation done in {(time.perf_counter() - t0) * 1000:.0f} ms")

        if not self.model.config.is_encoder_decoder:
            generated_ids = [
                out_ids[len(in_ids) :]
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]

        return self.processor.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
