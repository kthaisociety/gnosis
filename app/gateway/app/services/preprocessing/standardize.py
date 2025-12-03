"""
To do:
- 🗸 Resize image to standard size (pad long side with white to make perfect square)
- Fix offset (rotate image to correct orientation)
- Lines and dots consistent size.
"""

import cv2
import numpy as np

DEFAULT_TARGET_SIZE = (672, 672)
DEFAULT_FILL_COLOR = (255, 255, 255)


def standardize_image_size(
    img: np.ndarray, target_size=DEFAULT_TARGET_SIZE, fill_color=DEFAULT_FILL_COLOR
) -> np.ndarray:
    """
    Resize an image to a target size with preserved aspect ratio and padding.

    Args:
        img (np.ndarray): Input image (BGR).
        target_size (tuple): Desired (height, width).
        fill_color (tuple): Background color for padding (default white).

    Returns:
        np.ndarray: Resized and padded image.
    """
    h, w = img.shape[:2]
    target_h, target_w = target_size

    # Compute scaling factor to maintain aspect ratio
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)

    # Resize while maintaining aspect ratio
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create padded background
    result = np.full((target_h, target_w, 3), fill_color, dtype=np.uint8)

    # Center the resized image on the padded background
    y_offset = (target_h - new_h) // 2
    x_offset = (target_w - new_w) // 2
    result[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

    return result


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Denoise, enhance, and standardize scanned plots for visual cleanup,
    feature extraction, and OCR-based metadata extraction.
    """
    # Step 1: Denoise (remove scanner grain)
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Step 2: Bilateral filter for edge-preserving smoothness
    smooth = cv2.bilateralFilter(denoised, 9, 75, 75)

    # Step 3: Contrast enhancement using CLAHE
    lab = cv2.cvtColor(smooth, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    enhanced = cv2.merge((l_clahe, a, b))

    contrast_enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    """
    blurred = cv2.GaussianBlur(img, (0, 0), 1.0)
    sharpened = cv2.addWeighted(img, 1 + 1.8, blurred, -1.8, 0)
    """
    return contrast_enhanced
