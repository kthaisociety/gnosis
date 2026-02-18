"""
Modal deployment script for Gnosis VLM inference service.

Deploy: modal deploy modal_app.py
Test:   modal run modal_app.py
Pre-download model: modal run modal_app.py::download_model --model-name "nanonets/Nanonets-OCR-s"
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import modal
from pydantic import BaseModel

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not required

# =============================================================================
# Shared Models - Define here for consistent serialization between Modal and gateway
# These MUST match lib/src/lib/models/vlm_models.py exactly!
# =============================================================================


class DataPoint(BaseModel):
    x: float
    y: float


class VLMOutput(BaseModel):
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    legend: Optional[List[str]] = None
    data: List[DataPoint]


class InferenceConfig(BaseModel):
    model_name: str
    output_schema_name: Optional[str] = None
    use_gpu: Optional[bool] = None
    dtype: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[float] = None
    api_key: Optional[str] = None
    max_model_len: Optional[int] = None
    model_class: Optional[str] = None
    device_map: Optional[str] = None
    return_tensors: Optional[str] = None
    padding: Optional[str] = None
    attn_implementation: Optional[str] = None


# =============================================================================
# Authentication
# =============================================================================
if not (os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET")):
    print(
        "[INFO] No Modal token credentials found. "
        "If running non-interactively, set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET."
    )

# =============================================================================
# App Configuration
# =============================================================================
app = modal.App("gnosis-infer-app")

# GPU configuration via environment variables
GPU_TYPE = os.getenv("GPU_TYPE", "L4")
GPU_COUNT = int(os.getenv("GPU_COUNT", "4"))

# Resolve paths - now in vlm_server, paths are simpler
SCRIPT_DIR = Path(__file__).resolve().parent
VLM_SERVER_SRC = SCRIPT_DIR / "src" / "vlm_server"
LIB_SRC = SCRIPT_DIR.parent.parent / "lib" / "src" / "lib"
EVAL_SRC = SCRIPT_DIR.parent.parent / "services" / "eval" / "src"

# Validate paths exist
if not VLM_SERVER_SRC.exists():
    print(f"Warning: VLM server source not found at {VLM_SERVER_SRC}")
if not LIB_SRC.exists():
    print(f"Warning: Lib source not found at {LIB_SRC}")
if not EVAL_SRC.exists():
    print(f"Warning: Eval source not found at {EVAL_SRC}")

# Model cache volume
model_volume = modal.Volume.from_name("gnosis-models-cache", create_if_missing=True)
MODEL_CACHE_DIR = "/models"

# =============================================================================
# Container Image - Use CUDA image for flash-attn compilation
# =============================================================================
# Option 1: Use CUDA devel image for flash-attn
# Option 2: Skip flash-attn and use sdpa

USE_FLASH_ATTN = False  # True TAKES FUCKING AGES AND IM PATIENT ENOUGH IMO

if USE_FLASH_ATTN:
    # CUDA development image with nvcc for flash-attn compilation
    image = (
        modal.Image.from_registry(
            "nvidia/cuda:12.1.0-devel-ubuntu22.04",
            add_python="3.12",
        )
        .env(
            {
                "HF_HOME": MODEL_CACHE_DIR,
                "PYTHONPATH": "/root/vlm_server:/root/lib:/root/eval_service",
            }
        )
        .pip_install(
            "packaging",
            "ninja",
            "wheel",
            "torch>=2.1.0",
            "torchvision>=0.16.0",
            "transformers>=4.40.0",
            "accelerate>=0.27.0",
            "huggingface-hub>=0.20.0",
            "tokenizers>=0.15.0",
            "Pillow>=10.0.0",
            "pydantic>=2.0.0",
            "google-genai>=1.0.0",
            "python-dotenv>=1.0.0",
            "psycopg[binary]>=3.1.0",
            "psycopg-pool>=3.1.0",
            "openai>=1.0.0",
        )
        # Install flash-attn using run_commands so torch is available
        .run_commands("pip install flash-attn>=2.5.0 --no-build-isolation")
        .add_local_dir(str(VLM_SERVER_SRC), remote_path="/root/vlm_server")
        .add_local_dir(str(LIB_SRC), remote_path="/root/lib")
        .add_local_dir(str(EVAL_SRC), remote_path="/root/eval_service")
    )
else:
    # Standard image without flash-attn (uses sdpa for attention)
    image = (
        modal.Image.debian_slim(python_version="3.12")
        .env(
            {
                "HF_HOME": MODEL_CACHE_DIR,
                "PYTHONPATH": "/root/vlm_server:/root/lib:/root/eval_service",
                "BUILD_VERSION": "2026-01-28-v16",
            }
        )
        .pip_install(
            "torch>=2.1.0",
            "torchvision>=0.16.0",
            "transformers>=4.40.0",
            "accelerate>=0.27.0",
            "huggingface-hub>=0.20.0",
            "tokenizers>=0.15.0",
            "Pillow>=10.0.0",
            "pydantic>=2.0.0",
            "google-genai>=1.0.0",
            "python-dotenv>=1.0.0",
            "psycopg[binary]>=3.1.0",
            "psycopg-pool>=3.1.0",
            "openai>=1.0.0",
            "opencv-python-headless>=4.8.0",
            "boto3>=1.26.0",
            "scipy>=1.10.0",
            "grpcio>=1.50.0",
            "requests>=2.28.0",
            "python-Levenshtein>=0.21.0",
        )
        .add_local_dir(str(VLM_SERVER_SRC), remote_path="/root/vlm_server")
        .add_local_dir(str(LIB_SRC), remote_path="/root/lib")
        .add_local_dir(str(EVAL_SRC), remote_path="/root/eval_service")
    )

# Default attention implementation based on flash-attn availability
DEFAULT_ATTN_IMPL = "flash_attention_2" if USE_FLASH_ATTN else "sdpa"


# =============================================================================
# OCR Inference Class
# =============================================================================
@app.cls(
    gpu=f"{GPU_TYPE}:{GPU_COUNT}" if GPU_COUNT > 1 else GPU_TYPE,
    timeout=600,
    image=image,
    volumes={MODEL_CACHE_DIR: model_volume},
    scaledown_window=300,  # Keep container warm for 5 minutes
    secrets=[modal.Secret.from_name("huggingface-secret")],
)
@modal.concurrent(max_inputs=10)
class OCRInference:
    """Modal class for VLM OCR inference using vlm_server code."""

    @modal.enter()
    def setup(self):
        """Called once when container starts - load model."""
        import torch

        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(
                f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
            )

        # Pre-load default model
        model_name = "nanonets/Nanonets-OCR-s"
        print(f"Pre-loading model: {model_name}")

        try:
            from inference.main import download_model

            download_model(model_name)
            print(f"Model {model_name} ready")
        except Exception as e:
            print(f"Warning: Could not pre-load model: {e}")

    @modal.method()
    def infer(
        self,
        images_bytes: List[bytes],
        config: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> List[str]:
        """
        Main inference method using vlm_server inference code.

        Args:
            images_bytes: List of image bytes
            config: Inference configuration dict
            prompt: Optional prompt override

        Returns:
            List of raw text strings, one per input image.
        """
        import io
        import time

        # Import from mounted vlm_server and lib code
        from inference.main import make_model
        from lib.models.vlm import InferenceConfig as VLMInferenceConfig, ModelInfo
        from PIL import Image

        start = time.time()

        # Convert dict to InferenceConfig, injecting prompt if provided
        if prompt:
            config = {**config, "prompt": prompt}
        inf_config = VLMInferenceConfig(**config)

        # Build ModelInfo directly — avoids a DB round-trip from the container.
        # inference_class maps to the branch in vlm_server/inference/main.py:make_model:
        #   "transformers" → Transformer, "gemini" → Gemini, "gpt" → GPT
        _MODEL_REGISTRY = {
            "nanonets/Nanonets-OCR-s": ("transformers", "transformers"),
            "gemini-2.5-flash": ("api", "gemini"),
        }
        inference_type, inference_class = _MODEL_REGISTRY.get(
            inf_config.model_name, ("transformers", "transformers")
        )
        model_info = ModelInfo(
            model_name=inf_config.model_name,
            inference_type=inference_type,
            inference_class=inference_class,
            requires_gpu=inf_config.use_gpu,
        )
        model = make_model(model_info, inf_config)

        # Run inference on each image, collecting text results
        results = []
        for img_bytes in images_bytes:
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            raw_text = model.run(image, inf_config.prompt)
            results.append(raw_text)

        print(f"Inference completed in {time.time() - start:.2f}s")
        return results


# =============================================================================
# Utility: Pre-download model to cache
# =============================================================================
@app.function(
    timeout=1800,
    image=image,
    volumes={MODEL_CACHE_DIR: model_volume},
)
def download_model(model_name: str = "nanonets/Nanonets-OCR-s"):
    """
    Pre-download a model to the Modal volume for faster cold starts.

    Usage: modal run modal_app.py::download_model --model-name "nanonets/Nanonets-OCR-s"
    """
    from inference.main import download_model as dl_model

    print(f"Downloading model: {model_name}")
    dl_model(model_name)

    # Commit to volume
    model_volume.commit()
    print(f"Model {model_name} downloaded and cached!")


# =============================================================================
# Local entrypoint for testing
# =============================================================================
@app.local_entrypoint()
def main():
    """Test the Modal app."""
    print("Testing OCRInference...")

    # Create a simple test image
    import io

    from PIL import Image

    img = Image.new("RGB", (100, 100), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    config = {
        "model_name": "nanonets/Nanonets-OCR-s",
        "prompt": "Extract all text and data from this image.",
        "model_class": "AutoModelForImageTextToText",
        "use_gpu": True,
        "attn_implementation": DEFAULT_ATTN_IMPL,
        "max_tokens": 512,
    }

    result = OCRInference().infer.remote([img_bytes], config)
    print(f"Result: {result}")
