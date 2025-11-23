#!/usr/bin/env python3
"""Test script to run inference on test images from data/ directory."""

import os
import sys
import asyncio
from pathlib import Path
import httpx

# Get paths
CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent.parent.parent
TEST_IMAGES_DIR = ROOT_DIR / "data" / "images" / "images_processed"

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/process")


async def test_inference(image_path: Path, runner: str = "modal"):
    """Test inference on a single image."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {image_path.name} (runner={runner})")
    print(f"{'=' * 60}")

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/png")}
                params = {"runner": runner}
                response = await client.post(API_URL, files=files, params=params)

            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"   Inference time: {result.get('inference_time_ms', 'N/A')} ms")
                if result.get("html"):
                    print(f"   HTML length: {len(result['html'])} chars")
                if result.get("json_data"):
                    print(f"   JSON length: {len(result['json_data'])} chars")
                    print(f"   JSON preview: {result['json_data'][:200]}...")
                if result.get("text"):
                    print(f"   Text preview: {result['text'][:100]}...")
                if result.get("markdown"):
                    print(f"   Markdown length: {len(result['markdown'])} chars")
                if result.get("csv"):
                    print(f"   CSV length: {len(result['csv'])} chars")
                return True
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run inference on all test images."""
    if not TEST_IMAGES_DIR.exists():
        print(f"❌ Test images directory not found: {TEST_IMAGES_DIR}")
        sys.exit(1)

    image_files = list(TEST_IMAGES_DIR.glob("*.png"))
    if not image_files:
        print(f"❌ No PNG images found in {TEST_IMAGES_DIR}")
        sys.exit(1)

    print(f"Found {len(image_files)} test images")
    print(f"API URL: {API_URL}")
    print(
        "\nMake sure the server is running: uv run uvicorn app.server:app --host 127.0.0.1 --port 8000"
    )

    # Test with modal runner
    runner = os.getenv("RUNNER", "modal")
    print(f"\n{'=' * 60}")
    print(f"Testing with runner: {runner}")
    print(f"{'=' * 60}")

    results = []
    for img_path in sorted(image_files):
        success = await test_inference(img_path, runner=runner)
        results.append((img_path.name, success))

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"{'=' * 60}")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    # Count successes
    success_count = sum(1 for _, success in results if success)
    print(f"\n{success_count}/{len(results)} tests passed")


if __name__ == "__main__":
    asyncio.run(main())
