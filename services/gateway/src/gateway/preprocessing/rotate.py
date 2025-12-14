import cv2
import numpy as np
import math


def estimate_small_skew(
    gray: np.ndarray,
    canny_thresh1=50,
    canny_thresh2=150,
    hough_thresh=80,
    min_line_length_ratio=0.2,
    max_line_gap=5,
    allowed_angle_deg=10.0,
) -> float:
    """
    Estimate skew angle (in degrees) in range ±allowed_angle_deg assuming only small rotations.

    ASSUMING SMALL SKEW SUB 10 DEGREES
    """
    h, w = gray.shape[:2]
    # edge detection moment (this is where the magic happens)
    edges = cv2.Canny(gray, canny_thresh1, canny_thresh2, apertureSize=3)

    # hough lines (probabilistic)
    min_len = int(min_line_length_ratio * max(w, h))
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        hough_thresh,
        minLineLength=min_len,
        maxLineGap=max_line_gap,
    )
    if lines is None:
        return 0.0

    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            angle = 90.0
        else:
            angle = math.degrees(math.atan2(dy, dx))
        # normalize angle to lie between -90 and +90
        if angle > 90:
            angle -= 180
        if angle < -90:
            angle += 180

        # we expect primary axes lines ~0° (horizontal) or ~90° (vertical)
        # PICKING HORIZONTAL LINES AS SKEW CUES THIS IS ARBITRARY
        # so we accept only those lines whose abs(angle) ≤ allowed_angle or near 90° as skew cues
        if abs(angle) <= allowed_angle_deg:
            angles.append(angle)
        # Could also include vertical lines: |angle − 90°| ≤ allowed_angle_deg
        elif abs(abs(angle) - 90) <= allowed_angle_deg:
            # convert vertical lines to a "skew": if vertical is slightly slanted,
            # then skew = angle - 90 (or angle + 90) depending on sign
            # e.g. if angle = 90 + δ, then skew = δ
            # for simplicity, convert vertical deviation to standardized “horizontal skew”:
            if angle > 0:
                angles.append(angle - 90)
            else:
                angles.append(angle + 90)

    if len(angles) == 0:
        return 0.0

    # Use median (robust) to pick skew
    skew = float(np.median(angles))
    return skew


def deskew_small(
    img_gray: np.ndarray, max_allowed_deg: float = 10.0
) -> tuple[np.ndarray, float]:
    skew = estimate_small_skew(img_gray, allowed_angle_deg=max_allowed_deg)
    # If the skew is fuckass small just fogetabaoutit - thresholding
    if abs(skew) < 0.2:
        return img_gray, 0.0

    h, w = img_gray.shape[:2]
    center = (w / 2.0, h / 2.0)
    M = cv2.getRotationMatrix2D(center, skew, 1.0)
    rotated = cv2.warpAffine(
        img_gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated, skew
