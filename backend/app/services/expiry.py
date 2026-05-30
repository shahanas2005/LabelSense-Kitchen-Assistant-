from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable

from dateutil import parser as date_parser
from app.services.ocr import OCRLine


EXPIRY_LABELS = r"(?:exp(?:iry)?(?:\s*date)?|expires?(?:\s*on)?|best\s*before(?:\s*end)?|bbd?|use\s*by|sell\s*by|consum(?:e|ption)\s*by|date\s*of\s*expiry|expiry\s*date)"
MANUFACTURING_LABELS = r"(?:mfd(?:\s*date)?|mfg(?:\s*date)?|mfr|manufactur(?:ed|ing)(?:\s*date)?|date\s*of\s*manufacture|production\s*date|prod(?:uction)?\s*date|packed\s*on|pack(?:ed)?\s*date)"
WEIGHT_LABELS = r"(?:net\s*(?:weight|wt|wgt)|net\s*contents?|contents?|quantity|qty|gross\s*weight|weight|wt)"

OCR_NORMALIZATIONS = [
    (r"\bmfgdate\b", "mfg date"),
    (r"\bmfddate\b", "mfd date"),
    (r"\bmanufacturingdate\b", "manufacturing date"),
    (r"\bproductiondate\b", "production date"),
    (r"\bpackedon\b", "packed on"),
    (r"\bbestbefore\b", "best before"),
    (r"\buseby\b", "use by"),
    (r"\bsellby\b", "sell by"),
    (r"\b0ct\b", "oct"),
    (r"\b0tc\b", "oct"),
    (r"\b0ctober\b", "october"),
]

DATE_VALUE_PATTERN = r"(?:[0-3]?\d[\-/\.][01]?\d[\-/\.](?:\d{4}|\d{2})|\d{4}[\-/\.][01]?\d[\-/\.][0-3]?\d|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})"
DATE_PATTERNS = [
    re.compile(rf"\b{EXPIRY_LABELS}\b\s*[:\-]?\s*({DATE_VALUE_PATTERN})", re.I),
    re.compile(rf"\b{MANUFACTURING_LABELS}\b\s*[:\-]?\s*({DATE_VALUE_PATTERN})", re.I),
]

RELATIVE_PATTERN = re.compile(r"\b(?:best before|use by|sell by|bbd?)\s*[:\-]?\s*(\d+)\s*(day|days|month|months|year|years)\b", re.I)
OPENING_PATTERN = re.compile(r"\b(?:use within|consume within|use within\s+\d+\s+(?:day|days|month|months|year|years)\s+of\s+opening)\b", re.I)
MANUFACTURE_PATTERN = re.compile(rf"\b{MANUFACTURING_LABELS}\b\s*[:\-]?\s*({DATE_VALUE_PATTERN})", re.I)
DATE_TOKEN_PATTERN = re.compile(rf"\b({DATE_VALUE_PATTERN})\b", re.I)
NET_WEIGHT_PATTERN = re.compile(rf"\b{WEIGHT_LABELS}\b\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(kg|g|mg|lb|lbs|oz|ml|l|ltr|liter|litre|liters|litres|mcg)\b", re.I)
NET_WEIGHT_INLINE_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\s*(kg|g|mg|lb|lbs|oz|ml|l|ltr|liter|litre|liters|litres|mcg)\b", re.I)

KEYWORD_PRIORITY = {
    "exp": "detected_from_EXP",
    "expiry": "detected_from_EXP",
    "expires": "detected_from_EXP",
    "best before": "detected_from_BB",
    "bb": "detected_from_BB",
    "bbd": "detected_from_BB",
    "use by": "detected_from_BB",
    "sell by": "detected_from_BB",
    "mfg": "detected_from_MFG",
    "mfd": "detected_from_MFD",
    "mfr": "detected_from_MFR",
    "manufactur": "detected_from_MFG",
    "production": "detected_from_MFG",
    "packed on": "detected_from_MFG",
    "net weight": "detected_from_WEIGHT",
    "net wt": "detected_from_WEIGHT",
    "net contents": "detected_from_WEIGHT",
    "quantity": "detected_from_WEIGHT",
    "gross weight": "detected_from_WEIGHT",
}


@dataclass
class ExpiryResult:
    status: str
    expiry_date: str | None
    confidence: float
    source: str
    matched_text: str | None = None
    bbox: list[list[float]] | None = None
    message: str | None = None


@dataclass
class LabelFieldResult:
    field: str
    value: str | None
    source: str
    matched_text: str | None = None
    confidence: float = 0.0
    bbox: list[list[float]] | None = None


@dataclass
class LabelMetadataResult:
    expiry: ExpiryResult
    manufacturing_date: LabelFieldResult | None = None
    net_weight: LabelFieldResult | None = None
    detected_fields: list[dict] | None = None


def _normalize_date(value: str) -> date | None:
    cleaned = value.strip()
    for pattern in (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d.%m.%y",
        "%m/%Y",
        "%m-%Y",
        "%m.%Y",
    ):
        try:
            return datetime.strptime(cleaned, pattern).date()
        except ValueError:
            continue
    try:
        parsed = date_parser.parse(cleaned, dayfirst=True, fuzzy=True)
    except (ValueError, OverflowError):
        return None
    return parsed.date()


def _format_date(value: date) -> str:
    return value.strftime("%d-%m-%Y")


def _format_weight(amount: float, unit: str) -> str:
    normalized_unit = unit.lower()
    if normalized_unit in {"l", "ltr", "liter", "liters", "litre", "litres"}:
        normalized_unit = "L"
    return f"{amount:g} {normalized_unit}"


def _normalize_ocr_text(text: str) -> str:
    normalized = text
    for pattern, replacement in OCR_NORMALIZATIONS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.I)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _parse_duration(value: str, unit: str) -> timedelta:
    quantity = int(value)
    unit = unit.lower()
    if unit.startswith("year"):
        return timedelta(days=quantity * 365)
    if unit.startswith("month"):
        return timedelta(days=quantity * 30)
    return timedelta(days=quantity)


def _match_source(text: str) -> str:
    lowered = text.lower()
    for keyword, source in KEYWORD_PRIORITY.items():
        if keyword in lowered:
            return source
    return "detected_from_OCR"


def _line_list(lines: Iterable[OCRLine] | None) -> list[OCRLine]:
    return list(lines or [])


def _find_weight_match(text: str, lines: Iterable[OCRLine] | None = None) -> LabelFieldResult | None:
    for line in _line_list(lines):
        normalized_line = _normalize_ocr_text(" ".join(line.text.split()))
        match = NET_WEIGHT_PATTERN.search(normalized_line)
        if match:
            return LabelFieldResult(
                field="net_weight",
                value=_format_weight(float(match.group(1)), match.group(2)),
                source=_match_source(normalized_line),
                matched_text=match.group(0),
                confidence=min(0.95, 0.72 + (line.confidence * 0.25)),
                bbox=line.bbox,
            )

        lowered_line = normalized_line.lower()
        if any(keyword in lowered_line for keyword in ("weight", "wt", "qty", "quantity", "contents")):
            match = NET_WEIGHT_INLINE_PATTERN.search(normalized_line)
            if match:
                return LabelFieldResult(
                    field="net_weight",
                    value=_format_weight(float(match.group(1)), match.group(2)),
                    source=_match_source(normalized_line),
                    matched_text=match.group(0),
                    confidence=min(0.88, 0.55 + (line.confidence * 0.2)),
                    bbox=line.bbox,
                )

    match = NET_WEIGHT_PATTERN.search(_normalize_ocr_text(text))
    if match:
        return LabelFieldResult(
            field="net_weight",
            value=_format_weight(float(match.group(1)), match.group(2)),
            source=_match_source(match.group(0)),
            matched_text=match.group(0),
            confidence=0.82,
        )
    return None


def _find_label_date(text: str, lines: Iterable[OCRLine] | None, pattern: re.Pattern[str], field_name: str) -> LabelFieldResult | None:
    for line in _line_list(lines):
        normalized_line = _normalize_ocr_text(" ".join(line.text.split()))
        match = pattern.search(normalized_line)
        if match:
            parsed_date = _normalize_date(match.group(1))
            if parsed_date:
                return LabelFieldResult(
                    field=field_name,
                    value=_format_date(parsed_date),
                    source=_match_source(normalized_line),
                    matched_text=match.group(0),
                    confidence=min(0.98, 0.74 + (line.confidence * 0.3)),
                    bbox=line.bbox,
                )

    match = pattern.search(_normalize_ocr_text(text))
    if match:
        parsed_date = _normalize_date(match.group(1))
        if parsed_date:
            return LabelFieldResult(
                field=field_name,
                value=_format_date(parsed_date),
                source=_match_source(match.group(0)),
                matched_text=match.group(0),
                confidence=0.95,
            )
    return None


def _classify_date(expiry_date: date, matched_text: str, confidence: float, near_expiry_days: int, source: str, bbox: list[list[float]] | None = None) -> ExpiryResult:
    today = datetime.utcnow().date()
    delta = (expiry_date - today).days
    if delta < 0:
        status = "Expired"
    elif delta <= near_expiry_days:
        status = "Near Expiry"
    else:
        status = "Safe"
    return ExpiryResult(status=status, expiry_date=_format_date(expiry_date), confidence=confidence, source=source, matched_text=matched_text, bbox=bbox)


def _best_explicit_match(lines: Iterable[OCRLine], near_expiry_days: int) -> ExpiryResult | None:
    for line in lines:
        normalized_line = " ".join(line.text.split())
        for pattern in DATE_PATTERNS:
            match = pattern.search(normalized_line)
            if match:
                expiry_date = _normalize_date(match.group(1))
                if expiry_date:
                    source = _match_source(normalized_line)
                    confidence = min(0.98, 0.74 + (line.confidence * 0.3))
                    return _classify_date(expiry_date, match.group(0), confidence, near_expiry_days, source=source, bbox=line.bbox)

        for match in DATE_TOKEN_PATTERN.finditer(normalized_line):
            expiry_date = _normalize_date(match.group(1))
            if expiry_date:
                source = _match_source(normalized_line)
                confidence = min(0.9, 0.55 + (line.confidence * 0.25))
                return _classify_date(expiry_date, match.group(0), confidence, near_expiry_days, source=source, bbox=line.bbox)
    return None


def parse_dates(text: str, lines: list[OCRLine] | None = None, near_expiry_days: int = 30) -> ExpiryResult:
    normalized_text = _normalize_ocr_text(" ".join(text.split()))
    lowered_text = normalized_text.lower()

    manufacture = MANUFACTURE_PATTERN.search(normalized_text)
    direct_relative = RELATIVE_PATTERN.search(normalized_text)
    if manufacture and direct_relative:
        mfd_date = _normalize_date(manufacture.group(1))
        if mfd_date:
            expiry_date = mfd_date + _parse_duration(direct_relative.group(1), direct_relative.group(2))
            source = "detected_from_MFG_PLUS_DURATION"
            confidence = 0.9
            return _classify_date(expiry_date, f"{manufacture.group(0)} + {direct_relative.group(0)}", confidence, near_expiry_days, source=source)

    if lines:
        explicit = _best_explicit_match(lines, near_expiry_days=near_expiry_days)
        if explicit:
            return explicit

    for pattern in DATE_PATTERNS:
        match = pattern.search(normalized_text)
        if match:
            expiry_date = _normalize_date(match.group(1))
            if expiry_date:
                source = _match_source(match.group(0))
                return _classify_date(expiry_date, match.group(0), confidence=0.95, near_expiry_days=near_expiry_days, source=source)

    if direct_relative and any(keyword in normalized_text.lower() for keyword in ("best before", "bb", "bbd", "use by", "sell by")):
        # Without a manufacture/opening date this is still useful as a consumer-facing horizon.
        horizon = datetime.utcnow().date() + _parse_duration(direct_relative.group(1), direct_relative.group(2))
        return _classify_date(horizon, direct_relative.group(0), confidence=0.66, near_expiry_days=near_expiry_days, source="detected_from_RELATIVE_BB")

    if manufacture:
        mfd_date = _normalize_date(manufacture.group(1))
        if mfd_date:
            expiry_date = mfd_date + timedelta(days=365)
            return _classify_date(expiry_date, manufacture.group(0), confidence=0.72, near_expiry_days=near_expiry_days, source="detected_from_MFG")

    if OPENING_PATTERN.search(normalized_text):
        return ExpiryResult(
            status="Unknown",
            expiry_date=None,
            confidence=0.4,
            source="detected_from_RELATIVE_OPENING",
            message="Opening-based shelf life was detected, but no opening date was present.",
        )

    if lines:
        for line in lines:
            line_text = line.text.strip()
            if line_text and any(keyword in line_text.lower() for keyword in ("exp", "expiry", "bb", "best before", "use by", "sell by", "mfg", "mfd", "mfr", "manufactured", "manufacturing", "packed on", "production", "net weight", "weight", "wt", "qty", "quantity")):
                return ExpiryResult(
                    status="Unknown",
                    expiry_date=None,
                    confidence=max(0.25, min(0.45, line.confidence)),
                    source="detected_from_KEYWORD_ONLY",
                    matched_text=line_text,
                    bbox=line.bbox,
                    message="Expiry keyword found, but no reliable date was extracted.",
                )

    return ExpiryResult(
        status="Unknown",
        expiry_date=None,
        confidence=0.2,
        source="not_detected",
        message="Expiry not detected clearly. Please retake the image with better lighting and focus.",
    )


def extract_label_metadata(text: str, lines: list[OCRLine] | None = None, near_expiry_days: int = 30) -> LabelMetadataResult:
    normalized_text = " ".join(text.split())
    expiry = parse_dates(text=normalized_text, lines=lines, near_expiry_days=near_expiry_days)
    manufacturing_date = _find_label_date(normalized_text, lines, MANUFACTURE_PATTERN, "manufacturing_date")
    net_weight = _find_weight_match(normalized_text, lines)

    detected_fields: list[dict] = []
    if expiry.expiry_date:
        detected_fields.append({
            "field": "expiry_date",
            "value": expiry.expiry_date,
            "source": expiry.source,
            "matched_text": expiry.matched_text,
            "confidence": expiry.confidence,
        })
    if manufacturing_date and manufacturing_date.value:
        detected_fields.append({
            "field": manufacturing_date.field,
            "value": manufacturing_date.value,
            "source": manufacturing_date.source,
            "matched_text": manufacturing_date.matched_text,
            "confidence": manufacturing_date.confidence,
        })
    if net_weight and net_weight.value:
        detected_fields.append({
            "field": net_weight.field,
            "value": net_weight.value,
            "source": net_weight.source,
            "matched_text": net_weight.matched_text,
            "confidence": net_weight.confidence,
        })

    return LabelMetadataResult(
        expiry=expiry,
        manufacturing_date=manufacturing_date,
        net_weight=net_weight,
        detected_fields=detected_fields,
    )


def compute_expiry(text: str, lines: list[OCRLine] | None = None, near_expiry_days: int = 30) -> ExpiryResult:
    return parse_dates(text=text, lines=lines, near_expiry_days=near_expiry_days)


def detect_expiry(text: str, near_expiry_days: int = 30) -> ExpiryResult:
    return compute_expiry(text=text, lines=None, near_expiry_days=near_expiry_days)
