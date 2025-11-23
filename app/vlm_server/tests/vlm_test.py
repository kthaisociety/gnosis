# run tests/vlm_tests.py from root dir (uv run test/vlm_tests.py)
# Tests infer() main-entry from src/infer/main.py

from PIL import Image
from dotenv import load_dotenv
import sys
import os
import io
import time

sys.path.append("src/")

from infer.prompts.prompts import get_prompt
import modal
from utils.logging import get_logger

from infer import infer, InferenceConfig
from infer import download_model

log = get_logger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def test_inference():
    images = []
    for path in os.listdir("tests/processed_images/"):
        images.append(Image.open(os.path.join("tests/processed_images/", path)))

    infer_config = InferenceConfig(model_name="nanonets/Nanonets-OCR-s", use_gpu=False)

    # infer_config = InferenceConfig(
    #    model_name="gemini-2.5-flash",
    #    api_key=GEMINI_API_KEY
    # )

    result = infer([images[3]], infer_config)
    print(result)


def test_download():
    download_model("nanonets/Nanonets-OCR-s")


def ensure_modal_auth():
    if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
        # Already set
        return

    load_dotenv()
    modal_token_id = os.getenv("MODAL_TOKEN_ID")
    modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")

    if not (modal_token_id and modal_token_secret):
        raise RuntimeError(
            "Modal credentials not found. Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env"
        )

    # Explicitly configure Modal client
    modal.configure(token_id=modal_token_id, token_secret=modal_token_secret)
    print("Modal authenticated via .env credentials.")


def test_modal_inference():
    print("\n" + "=" * 60)
    print("MODAL INFERENCE TEST")
    print("=" * 60)

    test_start = time.time()

    SYSTEM_PROMPT = get_prompt("default")

    # Timer: Function loading
    load_start = time.time()

    # setup Modal app with token
    ensure_modal_auth()

    # Look up the deployed OCRInference class using Modal's Cls.from_name API
    OCRInference = modal.Cls.from_name("gnosis-infer-app", "OCRInference")

    load_time = time.time() - load_start
    log.info("Loaded Modal function: OCRInference (took %.2fs)", load_time)
    print(f"⏱️  Function load time: {load_time:.2f}s")

    # Timer: Image loading and preparation
    prep_start = time.time()
    images = []
    for path in os.listdir("tests/processed_images/"):
        images.append(Image.open(os.path.join("tests/processed_images/", path)))

    # Configure for Modal deployment with GPU (using sdpa attention - no flash-attn required)
    infer_config = InferenceConfig(
        model_name="nanonets/Nanonets-OCR-s",
        use_gpu=True,
        attn_implementation="sdpa",  # Use PyTorch's native sdpa instead of flash_attention_2
    )

    # Convert PIL Image to bytes for serialization
    img_bytes_list = []
    for img in [images[3]]:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes_list.append(buf.getvalue())

    prep_time = time.time() - prep_start
    print(f"⏱️  Image preparation time: {prep_time:.2f}s")
    print(f"📊 Image size: {len(img_bytes_list[0]) / 1024:.2f} KB")

    # Timer: Remote inference call
    print("\n🚀 Calling remote Modal inference...")
    inference_start = time.time()
    result = OCRInference().infer.remote(
        img_bytes_list, infer_config.model_dump(), SYSTEM_PROMPT
    )
    inference_time = time.time() - inference_start

    print(f"⏱️  Remote inference time: {inference_time:.2f}s")
    print("\n📋 Result:")
    print(result)

    # Total test time
    test_time = time.time() - test_start
    print(f"\n{'=' * 60}")
    print(f"⏱️  TOTAL TEST TIME: {test_time:.2f}s")
    print(f"{'=' * 60}\n")

    # Breakdown
    print("Time Breakdown:")
    print(
        f"  - Function loading:     {load_time:7.2f}s ({load_time / test_time * 100:5.1f}%)"
    )
    print(
        f"  - Image preparation:    {prep_time:7.2f}s ({prep_time / test_time * 100:5.1f}%)"
    )
    print(
        f"  - Remote inference:     {inference_time:7.2f}s ({inference_time / test_time * 100:5.1f}%)"
    )
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    # test_download()
    # test_inference()
    test_modal_inference()
