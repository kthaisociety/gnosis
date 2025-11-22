import os
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from .standardize import standardize_image_size, preprocess_image
from .rotate import deskew_small

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))


def process_image(img: np.ndarray) -> np.ndarray:
    standardized = standardize_image_size(img)
    processed = preprocess_image(standardized)
    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    deskewed, _angle = deskew_small(gray)
    return deskewed


"""Batch/CLI entrypoint logic. Per-request processing lives in utils.processbytes."""


def process_one(filename, input_output_dir, output_dir):
    img_path = os.path.join(input_output_dir, filename)
    img = cv2.imread(img_path)

    if img is None:
        logger.info(f"Skipping invalid file: {filename}")
        return filename, None

    # run pipeline
    logger.info(f"Processing image: {filename}")
    out = process_image(img)
    cv2.imwrite(os.path.join(output_dir, filename), out)

    # saving
    logger.info(f"Processed and saved: {filename}")
    return filename, 0.0


def main():
    # specify same input and output directory to overwrite images
    input_output_dir = os.path.join(ROOT_DIR, "data", "images", "images_raw")
    output_dir = os.path.join(ROOT_DIR, "data", "images", "images_processed")
    os.makedirs(output_dir, exist_ok=True)

    files = [f for f in os.listdir(input_output_dir)]
    if not files:
        logger.info("No input files found.")
        return

    max_workers = min(32, (os.cpu_count() or 4) * 2)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_one, f, input_output_dir, output_dir): f
            for f in files
        }
        for fut in as_completed(futures):
            fname = futures[fut]
            try:
                _, angle = fut.result()
                if angle is None:
                    continue
            except Exception as e:
                logger.exception(f"Failed processing {fname}: {e}")


if __name__ == "__main__":
    main()
