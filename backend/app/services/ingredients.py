from __future__ import annotations

import re

INGREDIENT_HEADER_PATTERN = re.compile(r"\bingredients?\b\s*[:\-]?")
SPLIT_PATTERN = re.compile(r"[,;\n]|\b(?:and|with|contains)\b", re.I)

NEGATION_WORDS = {"may contain", "contains", "allergen info"}

NORMALIZATION_MAP = {
    "sugar": "Sugar",
    "glucose": "Glucose",
    "fructose": "Fructose",
    "palm oil": "Palm Oil",
    "palmolein": "Palm Oil",
    "vegetable oil": "Vegetable Oil",
    "preservative": "Preservatives",
    "sodium benzoate": "Sodium Benzoate",
    "potassium sorbate": "Potassium Sorbate",
    "artificial flavor": "Artificial Flavour",
    "artificial flavour": "Artificial Flavour",
    "artificial color": "Artificial Colour",
    "artificial colour": "Artificial Colour",
    "lactose": "Lactose",
    "gluten": "Gluten",
    "nuts": "Nuts",
}


def extract_ingredients(text: str) -> list[str]:
    normalized_text = " ".join(text.split())
    candidate = _extract_ingredient_block(normalized_text)
    raw_items = [segment.strip(" .:-").lower() for segment in SPLIT_PATTERN.split(candidate)]
    items: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        if len(item) < 2:
            continue
        normalized = NORMALIZATION_MAP.get(item, item.title())
        key = normalized.lower()
        if key not in seen and normalized:
            seen.add(key)
            items.append(normalized)
    return items[:15]


def _extract_ingredient_block(text: str) -> str:
    lowered = text.lower()
    for match in INGREDIENT_HEADER_PATTERN.finditer(lowered):
        candidate = text[match.end():]
        trimmed = _trim_to_next_section(candidate)
        if len(trimmed.split()) >= 2:
            return trimmed
    if "ingredients" in lowered:
        candidate = text[lowered.find("ingredients") + len("ingredients"):]
        return _trim_to_next_section(candidate)
    return _trim_to_next_section(text)


def _trim_to_next_section(text: str) -> str:
    section_markers = ["nutrition", "storage", "warning", "manufacturer", "expiry", "best before", "use by"]
    lowered = text.lower()
    stops = [lowered.find(marker) for marker in section_markers if lowered.find(marker) > 0]
    stop = min(stops) if stops else len(text)
    return text[:stop]
