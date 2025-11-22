#!/usr/bin/env python3
"""Test script to run inference on test images from data/ directory."""

import os
import sys
import asyncio
from pathlib import Path
import httpx

# Get paths
CURRENT_DIR = Path(__file__).parent
ROOT_DIR = CURRENT_DIR.parent
TEST_IMAGES_DIR = ROOT_DIR / "data" / "images" / "images_processed"

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/process")


async def test_inference(image_path: Path):
    """Test inference on a single image."""
    print(f"\n{'='*60}")
    print(f"Testing: {image_path.name}")
    print(f"{'='*60}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/png")}
                response = await client.post(API_URL, files=files)

            if response.status_code == 200:
                result = response.json()
                print(result)
                print(f"✅ Success!")
                print(f"   Inference time: {result.get('inference_time_ms', 'N/A')} ms")
                if result.get("html"):
                    print(f"   HTML length: {len(result['html'])} chars")
                if result.get("json"):
                    print(f"   JSON length: {len(result['json'])} chars")
                if result.get("text"):
                    print(f"   Text preview: {result['text'][:100]}...")
                return True
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Exception: {e}")
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
    print(f"\nMake sure the server is running: uv run server.py")

    results = []
    for img_path in sorted(image_files):
        success = await test_inference(img_path)
        results.append((img_path.name, success))

    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")


if __name__ == "__main__":
    asyncio.run(main())
