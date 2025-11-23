import os
from typing import List
from pathlib import Path
import modal
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------------------
# 1. Authentication: Prefer Proxy Auth for CI/CD or headless environments
# -----------------------------------------------------------------------------
if not (os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET")):
    print(
        "[INFO] No Modal token credentials found. "
        "Set MODAL_TOKEN_ID + MODAL_TOKEN_SECRET."
    )

# Create app
app = modal.App("gnosis-infer-app")

# -----------------------------------------------------------------------------
# 2. Configuration: set GPU type/count and resolve paths
# -----------------------------------------------------------------------------
GPU_TYPE = os.getenv("GPU_TYPE", "L4")
GPU_COUNT = int(os.getenv("GPU_COUNT", "4"))

# Resolve paths relative to this file (compute/modal/)
scripts_dir = Path(__file__).resolve().parent

# Get the inference directory (parent of compute) to access:
# - compute/vlm_server/src/infer/
# - models.py
# - vlm.py
compute_dir = scripts_dir.parent  # compute/
inference_dir = compute_dir.parent  # inference/
repo_root = inference_dir

requirements_file = compute_dir / "requirements.txt"

# Fail fast if requirements.txt not found to provide clearer error during build
if not requirements_file.exists():
    raise FileNotFoundError(
        f"Expected requirements.txt at {requirements_file} but it was not found"
    )

# -----------------------------------------------------------------------------
# 3. Model caching via Modal Volume
# -----------------------------------------------------------------------------
model_volume = modal.Volume.from_name("gnosis-models-cache", create_if_missing=True)
MODEL_CACHE_DIR = "/models"


# -----------------------------------------------------------------------------
# 4. Image build definition: Python environment with dependencies
# -----------------------------------------------------------------------------
image = (
    modal.Image.debian_slim(python_version="3.11")
    .env(
        {
            "HF_HOME": MODEL_CACHE_DIR,
        }
    )
    .pip_install_from_requirements(str(requirements_file))
    .add_local_dir(repo_root, remote_path="/root/src")
)


# -----------------------------------------------------------------------------
# 5. OCR Inference class
# -----------------------------------------------------------------------------
@app.cls(
    gpu=f"{GPU_TYPE}:{GPU_COUNT}",
    timeout=600,
    image=image,
    volumes={MODEL_CACHE_DIR: model_volume},
    scaledown_window=300,  # Keep container warm for 5 minutes
)
@modal.concurrent(max_inputs=10)  # Allows concurrent requests on same container
class OCRInference:
    @modal.enter()
    def load_model(self):
        """Load model once when container starts - updated for sdpa attention"""
        import sys

        sys.path.insert(0, "/root/src/compute/vlm_server/src")
        from infer import download_model as dl_model
        from pathlib import Path

        # Pre-load the model into memory
        model_name = "nanonets/Nanonets-OCR-s"
        print(f"Loading model: {model_name}")

        # Check if model is already cached
        model_cache_path = Path(MODEL_CACHE_DIR) / "hub" / model_name.replace("/", "--")
        if model_cache_path.exists():
            print(f"Model {model_name} found in cache, skipping download")
        else:
            print(f"Model {model_name} not in cache, downloading...")

        dl_model(model_name)
        print("Model loaded and ready!")

    @modal.method()
    def infer(self, images_bytes: List[bytes], config: dict, prompt: str = None):
        """Run inference on images"""
        import sys
        import time

        sys.path.insert(0, "/root/src/compute/vlm_server/src")
        from infer.main import infer as run_infer
        from infer.vlm import InferenceConfig
        from PIL import Image
        import io

        start = time.time()

        # Convert bytes to PIL Images
        images = [Image.open(io.BytesIO(img_bytes)) for img_bytes in images_bytes]

        # Convert dict to InferenceConfig
        if isinstance(config, dict):
            config = InferenceConfig(**config)

        # Run inference
        result = run_infer(images, config, prompt)

        print(f"Inference completed in {time.time() - start:.2f}s")
        return result


# -----------------------------------------------------------------------------
# 6. Utility: Pre-download model
# -----------------------------------------------------------------------------
@app.function(
    timeout=1800,  # 30 minutes for downloading large models
    image=image,
    volumes={MODEL_CACHE_DIR: model_volume},
)
def download_model(model_name: str):
    """
    Pre-download a model to the Modal volume for faster cold starts.
    Usage:
    modal run \
        gnosis/app/src/services/inference/compute/modal/deploy.py::download_model \
        --model-name "nanonets/Nanonets-OCR-s"
    """
    import sys

    sys.path.insert(0, "/root/src/compute/vlm_server/src")

    from infer import download_model as dl_model

    print(f"Downloading model: {model_name}")
    dl_model(model_name)

    # Commit the downloaded model to the volume
    model_volume.commit()
    print(f"Model {model_name} downloaded and cached successfully!")
