#!/usr/bin/env python3
"""Test script to run inference on test images from data/ directory."""

import sys
import asyncio
import json
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Get paths
CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent.parent.parent
TEST_IMAGES_DIR = ROOT_DIR / "data" / "images" / "processed"

API_URL = "http://127.0.0.1:8000/process"

# Test configurations
CONFIGS = {
    "modal": {
        "runner": "modal",
        "config": {
            "model_name": "nanonets/Nanonets-OCR-s",
            "prompt": "Extract all data from this image.",
            "use_gpu": True,
            "attn_implementation": "sdpa",
            "output_schema_name": "TableOutput",
        },
    },
    "local": {
        "runner": "local",
        "config": {
            "model_name": "gemini-2.5-flash",
            "api_key": os.getenv("GEMINI_API_KEY"),
#            "model_name": "nanonets/Nanonets-OCR-s",
            "prompt": "Extract all data from this image.",
            "use_gpu": False,
            "output_schema_name": "TableOutput",
        },
    },
}


async def test_inference(image_path: Path, config_name: str):
    """Test inference on a single image."""
    test_config = CONFIGS[config_name]

    print(f"\n{'='*60}")
    print(f"Testing: {image_path.name}")
    print(f"  Runner: {test_config['runner']}")
    print(f"  Model: {test_config['config']['model_name']}")
    print(f"  GPU: {test_config['config']['use_gpu']}")
    #    print(f"  Prompt: {test_config['prompt'][:50]}...")
    print(f"{'='*60}")

    try:
        config_json = json.dumps(test_config["config"])

        async with httpx.AsyncClient(timeout=600.0) as client:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/png")}
                data = {
                    "runner": test_config["runner"],
                    "config": config_json,
                    # "prompt": test_config['prompt'],
                }

                response = await client.post(API_URL, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"   Inference time: {result.get('inference_time_ms', 'N/A')} ms")

                if result.get("text"):
                    preview = result["text"][:200].replace("\n", " ")
                    print(f"   Text: {preview}...")
                return True
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_runner(runner_name: str, image_files: list):
    """Test a specific runner on all images."""
    print(f"\n{'#'*60}")
    print(f"# Testing Runner: {runner_name.upper()}")
    print(f"{'#'*60}")

    if runner_name == "local":
        print("\n⚠️  Ensure vlm_server is running (gRPC on port 50051):")
        print("   cd services/vlm_server && uv run python -m vlm_server.server\n")

    results = []
    for img_path in sorted(image_files)[:3]:  # Test first 3 images
        success = await test_inference(img_path, runner_name)
        results.append((img_path.name, success))

    return results


async def main():
    """Run inference tests on both runners."""
    if not TEST_IMAGES_DIR.exists():
        print(f"❌ Test images directory not found: {TEST_IMAGES_DIR}")
        sys.exit(1)

    image_files = list(TEST_IMAGES_DIR.glob("*.png"))
    if not image_files:
        print(f"❌ No PNG images found in {TEST_IMAGES_DIR}")
        sys.exit(1)

    print(f"Found {len(image_files)} test images")
    print(f"API URL: {API_URL}")
    print("\n⚠️  Ensure gateway is running:")
    print("   uv run uvicorn gateway.server:app --host 127.0.0.1 --port 8000")

    # Test both runners
    all_results = {}

    # Test Modal
    modal_results = await test_runner("modal", image_files)
    all_results["modal"] = modal_results

    # Test Local (gRPC)
    local_results = await test_runner("local", image_files)
    all_results["local"] = local_results

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")

    for runner_name, results in all_results.items():
        success_count = sum(1 for _, success in results if success)
        print(f"\n{runner_name.upper()}: {success_count}/{len(results)} passed")
        for name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {name}")


if __name__ == "__main__":
    asyncio.run(main())
