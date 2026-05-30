from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def _resize_for_ocr(frame: np.ndarray, target_max_dimension: int) -> np.ndarray:
    height, width = frame.shape[:2]
    scale = target_max_dimension / max(height, width)
    if scale <= 0:
        return frame
    if scale == 1.0:
        return frame
    interpolation = cv2.INTER_CUBIC if scale > 1.0 else cv2.INTER_AREA
    return cv2.resize(frame, (max(1, int(width * scale)), max(1, int(height * scale))), interpolation=interpolation)


def _enhance_contrast(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _sharpen(gray: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(gray, -1, kernel)


def _threshold(gray: np.ndarray) -> np.ndarray:
    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshold


def _adaptive_threshold(gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )


def preprocess_image(image: Image.Image, target_max_dimension: int = 2200) -> np.ndarray:
    rgb_image = image.convert("RGB")
    frame = np.array(rgb_image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = _resize_for_ocr(frame, target_max_dimension)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = _enhance_contrast(gray)
    gray = _sharpen(gray)
    return _threshold(gray)


def preprocess_image_variants(image: Image.Image) -> list[np.ndarray]:
    rgb_image = image.convert("RGB")
    frame = np.array(rgb_image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    variants: list[np.ndarray] = []
    for target in (1600, 2200):
        resized = _resize_for_ocr(frame.copy(), target)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = _enhance_contrast(gray)
        gray = _sharpen(gray)
        variants.append(gray)
        variants.append(_threshold(gray))
        variants.append(_adaptive_threshold(gray))
        variants.append(cv2.bitwise_not(_threshold(gray)))

    height, width = frame.shape[:2]
    band_height = max(1, height // 3)
    for band_index in range(3):
        top = band_index * band_height
        bottom = height if band_index == 2 else min(height, (band_index + 1) * band_height)
        band = frame[top:bottom, :]
        if band.size == 0:
            continue
        band = _resize_for_ocr(band, 2200)
        gray = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
        gray = _enhance_contrast(gray)
        gray = _sharpen(gray)
        variants.append(_threshold(gray))
        variants.append(_adaptive_threshold(gray))

    return variants
