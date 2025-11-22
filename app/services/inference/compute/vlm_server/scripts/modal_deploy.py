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
        "If you're running this non-interactively, set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET."
    )

# Create app
app = modal.App("gnosis-infer-app")

# -----------------------------------------------------------------------------
# 2. Configuration: set GPU type/count and resolve paths
# -----------------------------------------------------------------------------
GPU_TYPE = os.getenv("GPU_TYPE", "L4")
GPU_COUNT = int(os.getenv("GPU_COUNT", "4"))

# Resolve paths relative to this file (scripts/). We prefer a real 'src' folder discovered by walking up parents.
scripts_dir = Path(__file__).resolve().parent


# looks for src directory by walking up parents
def _find_src_dir(start: Path) -> Path | None:
    cur = start
    while True:
        candidate = cur / "src"
        if candidate.exists() and candidate.is_dir():
            return candidate
        if cur.parent == cur:
            return None
        cur = cur.parent


# Try several locations: script's parents, CWD parents, then env var fallback
src_candidate = _find_src_dir(scripts_dir) or _find_src_dir(Path.cwd())
if src_candidate is None:
    env_src = os.getenv("GNOSIS_SRC_PATH") or os.getenv("MODAL_SRC_PATH")
    if env_src:
        env_path = Path(env_src)
        if env_path.exists() and env_path.is_dir():
            src_candidate = env_path

if src_candidate is None:
    # Non-fatal fallback: use the original sibling path (may be valid in Modal build context).
    # Emit a clear warning instead of raising so local runs don't crash with FileNotFoundError.
    fallback = scripts_dir.parent / "src"
    print(
        f"Warning: could not locate 'src' by walking parents or env; using fallback {fallback!s}. "
        "If this is incorrect, set GNOSIS_SRC_PATH to the correct path."
    )
    src_dir = fallback
else:
    src_dir = src_candidate

repo_root = src_dir.parent
requirements_file = repo_root / "requirements-modal.txt"

# Fail fast if src not found to provide clearer error during build
if not src_dir.exists():
    raise FileNotFoundError(
        f"Expected src directory at {src_dir} but it was not found. Adjust paths accordingly."
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
    .add_local_dir(src_dir, remote_path="/root/src")
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

        sys.path.insert(0, "/root/src")
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

        sys.path.insert(0, "/root/src")
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
    Usage: modal run src/infer/modalDeploy.py::download_model --model-name "nanonets/Nanonets-OCR-s"
    """
    import sys

    sys.path.insert(0, "/root/src")

    from infer import download_model as dl_model

    print(f"Downloading model: {model_name}")
    dl_model(model_name)

    # Commit the downloaded model to the volume
    model_volume.commit()
    print(f"Model {model_name} downloaded and cached successfully!")
