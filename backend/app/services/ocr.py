from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass

import numpy as np
from PIL import Image

from app.services.preprocess import preprocess_image, preprocess_image_variants


@dataclass
class OCRLine:
    text: str
    confidence: float
    bbox: list[list[float]] | None = None


@dataclass
class OCRResult:
    text: str
    confidence: float
    lines: list[OCRLine]
    source: str


@lru_cache(maxsize=1)
def _get_rapidocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
    except Exception:
        return None
    return RapidOCR()


def _run_rapidocr(image_array: np.ndarray) -> OCRResult:
    ocr = _get_rapidocr()
    if ocr is None:
        return OCRResult(text="", confidence=0.0, lines=[], source="rapidocr_unavailable")

    result, _ = ocr(image_array)
    if not result:
        return OCRResult(text="", confidence=0.0, lines=[], source="rapidocr")

    lines: list[OCRLine] = []
    texts: list[str] = []
    confidences: list[float] = []
    for item in result:
        bbox = None
        if len(item) >= 1 and isinstance(item[0], (list, tuple)):
            bbox = [[float(point[0]), float(point[1])] for point in item[0]]
        line_text = str(item[1]).strip() if len(item) >= 2 else ""
        line_confidence = float(item[2]) if len(item) >= 3 else 0.0
        if line_text:
            texts.append(line_text)
            confidences.append(line_confidence)
            lines.append(OCRLine(text=line_text, confidence=line_confidence, bbox=bbox))
    text = "\n".join(texts)
    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return OCRResult(text=text, confidence=confidence, lines=lines, source="rapidocr")


def _ocr_score(result: OCRResult) -> float:
    text_bonus = min(len(result.text), 400) / 1000
    return result.confidence + text_bonus


def _run_pytesseract(image_array: np.ndarray) -> OCRResult:
    try:
        import pytesseract
    except Exception:
        return OCRResult(text="", confidence=0.0, lines=[], source="pytesseract_unavailable")

    text = pytesseract.image_to_string(image_array)
    lines = [OCRLine(text=line.strip(), confidence=0.0, bbox=None) for line in text.splitlines() if line.strip()]
    return OCRResult(text=text.strip(), confidence=0.0, lines=lines, source="pytesseract")


def extract_text_from_image(image: Image.Image) -> OCRResult:
    variants = preprocess_image_variants(image)
    candidates: list[OCRResult] = []
    for variant in variants:
        rapid_result = _run_rapidocr(variant)
        if rapid_result.text:
            if rapid_result.confidence >= 0.82 or len(rapid_result.text.split()) >= 10:
                return rapid_result
            candidates.append(rapid_result)

    if candidates:
        candidates.sort(key=_ocr_score, reverse=True)
        return candidates[0]

    processed = preprocess_image(image)
    rapid_result = _run_rapidocr(processed)
    if rapid_result.text:
        return rapid_result

    return _run_pytesseract(processed)


def save_uploaded_image(image: Image.Image, target_path: Path) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(target_path)
    return str(target_path)
