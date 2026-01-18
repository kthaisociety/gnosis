#!/usr/bin/env python3
"""
Upload benchmark images to S3 + Neon database from a ground_truth.json file.

This script:
1. Reads ground_truth.json with ground truth data
2. Uploads images to Cloudflare R2 (UUID-based storage)
3. Creates records in Neon database

Usage:
    python scripts/process_and_upload_dataset.py --folder datasets/my_charts
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lib.db import close_db_pool
from eval.data import (
    create_dataset,
    get_dataset_by_name,
    upload_benchmark_image,
    ensure_s3_bucket_exists,
)
from eval.models import DatasetCreate

load_dotenv()


def load_ground_truth(dataset_path: str) -> Dict[str, Any]:
    """Load ground_truth.json file from dataset folder."""
    if not Path(dataset_path).exists():
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

    ground_truth_file = Path(dataset_path) / "ground_truth.json"
    if not ground_truth_file.exists():
        raise FileNotFoundError(f"Ground truth file not found: {ground_truth_file}")

    return json.loads(ground_truth_file.read_text())


def upload(folder_path: str, create_new_dataset: bool = False) -> Dict[str, Any]:
    """Upload images from ground truth to S3 and Neon."""
    folder = Path(folder_path)

    # Ensure S3 bucket exists
    if not ensure_s3_bucket_exists():
        raise RuntimeError("S3 bucket does not exist and could not be created")

    # Get dataset name from environment variable
    dataset_name = os.getenv("DATASET_NAME")
    if not dataset_name:
        raise ValueError(
            "DATASET_NAME not found in environment variables. Please set it in .env file."
        )

    # Load ground truth
    ground_truth = load_ground_truth(folder_path)

    # Get or create dataset
    if create_new_dataset:
        dataset = DatasetCreate(
            name=dataset_name,
            description=ground_truth.get("description"),
            version=ground_truth.get("version", "1.0"),
        )
        dataset_id = create_dataset(dataset)

        if not dataset_id:
            # Try to get existing dataset instead
            dataset = get_dataset_by_name(dataset_name)
            if dataset:
                dataset_id = dataset.dataset_id
            else:
                raise RuntimeError(
                    f"Failed to create or retrieve dataset '{dataset_name}'"
                )
    else:
        dataset = get_dataset_by_name(dataset_name)
        if not dataset:
            raise ValueError(f"Dataset '{dataset_name}' not found")
        dataset_id = dataset.dataset_id

    # Upload each image
    results = {"successful": [], "failed": []}

    total = len(ground_truth["images"])
    for i, item in enumerate(ground_truth["images"], 1):
        print(f"[{i}/{total}] Uploading {item['filename']}")

        image_path = folder / item["filename"]
        if not image_path.exists():
            print(f"Image file not found: {image_path}")
            results["failed"].append(
                {"filename": item["filename"], "error": "File not found"}
            )
            continue

        try:
            image_id = upload_benchmark_image(
                local_file_path=str(image_path),
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                image_type=item.get("image_type", "other"),
                ground_truth=item.get("ground_truth"),
                metadata=item.get("metadata", {}),
            )

            if image_id:
                print(f"Uploaded with ID: {image_id}")
                results["successful"].append(
                    {"filename": item["filename"], "image_id": str(image_id)}
                )
            else:
                print("Upload returned None")
                results["failed"].append(
                    {"filename": item["filename"], "error": "Upload returned None"}
                )

        except Exception as e:
            print(f"Upload failed: {e}")
            results["failed"].append({"filename": item["filename"], "error": str(e)})

    # Save upload log
    upload_log_path = folder / "upload_log.json"
    with open(upload_log_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nUpload log saved to {upload_log_path}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Upload chart/graph images to benchmark dataset from ground_truth.json"
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Path to folder containing images and ground_truth.json",
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("UPLOADING TO S3 AND NEON")
        print("=" * 60)

        results = upload(folder_path=args.folder, create_new_dataset=True)

        print("\n" + "=" * 60)
        print("UPLOAD SUMMARY")
        print("=" * 60)
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")

        if results["failed"]:
            print("\nFailed uploads:")
            for item in results["failed"]:
                print(f"  - {item['filename']}: {item['error']}")

        print("\nProcess complete.")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        close_db_pool()


if __name__ == "__main__":
    main()
