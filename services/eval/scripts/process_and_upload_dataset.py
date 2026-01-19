"""
Upload benchmark images to S3 + Neon database from a ground_truth.json file.

Usage:
    python scripts/process_and_upload_dataset.py --folder datasets/my_charts --dataset benchmark_v1
"""

import argparse
import json
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
    ground_truth_file = Path(dataset_path) / "ground_truth.json"
    if not ground_truth_file.exists():
        raise FileNotFoundError(f"Ground truth file not found: {ground_truth_file}")
    return json.loads(ground_truth_file.read_text())


def upload(folder_path: str, dataset_name: str, create_new: bool = False) -> Dict[str, Any]:
    folder = Path(folder_path)

    if not ensure_s3_bucket_exists():
        raise RuntimeError("S3 bucket does not exist and could not be created")

    ground_truth = load_ground_truth(folder_path)

    if create_new:
        dataset = DatasetCreate(
            name=dataset_name,
            description=ground_truth.get("description"),
            version=ground_truth.get("version", "1.0"),
        )
        dataset_id = create_dataset(dataset)
        if not dataset_id:
            dataset = get_dataset_by_name(dataset_name)
            if dataset:
                dataset_id = dataset.dataset_id
            else:
                raise RuntimeError(f"Failed to create or retrieve dataset '{dataset_name}'")
    else:
        dataset = get_dataset_by_name(dataset_name)
        if not dataset:
            raise ValueError(f"Dataset '{dataset_name}' not found")
        dataset_id = dataset.dataset_id

    results = {"successful": [], "failed": []}

    total = len(ground_truth["images"])
    for i, item in enumerate(ground_truth["images"], 1):
        print(f"[{i}/{total}] Uploading {item['filename']}")

        image_path = folder / item["filename"]
        if not image_path.exists():
            print(f"Image file not found: {image_path}")
            results["failed"].append({"filename": item["filename"], "error": "File not found"})
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
                results["successful"].append({"filename": item["filename"], "image_id": str(image_id)})
            else:
                print("Upload returned None")
                results["failed"].append({"filename": item["filename"], "error": "Upload returned None"})

        except Exception as e:
            print(f"Upload failed: {e}")
            results["failed"].append({"filename": item["filename"], "error": str(e)})

    upload_log_path = folder / "upload_log.json"
    with open(upload_log_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nUpload log saved to {upload_log_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Upload images to benchmark dataset")
    parser.add_argument("--folder", required=True, help="Path to folder with images and ground_truth.json")
    parser.add_argument("--dataset", required=True, help="Dataset name to upload to")
    args = parser.parse_args()

    try:
        print("=" * 60)
        print("UPLOADING TO S3 AND NEON")
        print("=" * 60)

        results = upload(folder_path=args.folder, dataset_name=args.dataset, create_new=True)

        print("\n" + "=" * 60)
        print("UPLOAD SUMMARY")
        print("=" * 60)
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")

        if results["failed"]:
            print("\nFailed uploads:")
            for item in results["failed"]:
                print(f"  - {item['filename']}: {item['error']}")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        close_db_pool()


if __name__ == "__main__":
    main()

