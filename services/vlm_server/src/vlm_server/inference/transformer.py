import time
from PIL import Image
from transformers import (
    AutoProcessor,
    AutoModelForImageTextToText,
)

from lib.models.vlm import InferenceConfig
from lib.utils.log import get_logger

logger = get_logger(__name__)

MODEL_CLASS = {"AutoModelForImageTextToText": AutoModelForImageTextToText}


class Transformer:
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.load_model()

    def load_model(self):
        model_name = self.config.model_name
        model_class = self.config.model_class
        use_gpu = self.config.use_gpu
        dtype = self.config.dtype

        # ensure device is configured
        device_map = self.config.device_map
        if device_map is None:
            device_map = "auto"

        # ensure attention matches gpu configuration, default on mismatch
        attn_implementation = self.config.attn_implementation
        if attn_implementation == "flash_attention_2" and not use_gpu:
            logger.warn("flash_attention_2 requires gpu, defaulting to sdpa")
            attn_implementation = "sdpa"

        # ensure model class is supported
        if model_class not in MODEL_CLASS:
            raise Exception(f"unsupported model class '{model_class}'")

        logger.info(f"loading {model_name}... (device={device_map})")
        t0 = time.perf_counter()

        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = MODEL_CLASS[model_class].from_pretrained(
            model_name=model_name,
            dtype=dtype,
            device_map=device_map,
            attn_implementation=attn_implementation,
        )

        logger.info(f"loaded {model_name} in {(time.perf_counter() - t0) * 1000:.1f}s")

    def run(self, image: Image, prompt: str) -> str:
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

        return_tensors = self.config.return_tensors
        padding = self.config.padding

        inputs = self.processor(
            text=[text], images=[image], padding=padding, return_tensors=return_tensors
        ).to(self.model.device)

        logger.info("generating...")
        t0 = time.perf_counter()

        max_tokens = self.config.max_tokens
        generated_ids = self.model.generate(**inputs, max_new_tokens=max_tokens)

        logger.info(f"generation done in {(time.perf_counter - t0) * 1000:.1f} ms")

        if not self.model.config.is_encoder_decoder:
            generated_ids = [
                out_ids[len(in_ids) :]
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]

        return self.processor.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
