from __future__ import annotations

from typing import Any, Dict, List


# Mapping keywords to canonical risks and default severities
KEYWORD_MAPPING: Dict[str, Dict[str, Any]] = {
    "sugar": {"risk": "diabetes", "reason": "Contains sugar", "severity": "medium"},
    "glucose": {"risk": "diabetes", "reason": "Contains glucose syrup", "severity": "medium"},
    "glucose syrup": {"risk": "diabetes", "reason": "Contains glucose syrup", "severity": "medium"},
    "fructose": {"risk": "diabetes", "reason": "Contains fructose", "severity": "medium"},
    "sodium": {"risk": "hypertension", "reason": "High sodium content", "severity": "medium"},
    "salt": {"risk": "hypertension", "reason": "High salt content", "severity": "medium"},
    "milk": {"risk": "lactose", "reason": "Contains milk/lactose", "severity": "high"},
    "lactose": {"risk": "lactose", "reason": "Contains lactose", "severity": "high"},
    "peanut": {"risk": "nuts", "reason": "Contains peanuts", "severity": "high"},
    "peanuts": {"risk": "nuts", "reason": "Contains peanuts", "severity": "high"},
    "almond": {"risk": "nuts", "reason": "Contains tree nuts", "severity": "high"},
    "nuts": {"risk": "nuts", "reason": "Contains nuts", "severity": "high"},
}


def analyze_ingredients(ingredients: List[str], raw_text: str) -> List[Dict[str, Any]]:
    """Analyze raw ingredients list and raw OCR text to find keyword matches.

    Returns a list of signals: {ingredient, keyword, risk, reason, severity, matched_text}
    """
    signals: List[Dict[str, Any]] = []
    lowered_text = raw_text.lower()
    for ing in ingredients:
        ing_l = ing.lower()
        for key, info in KEYWORD_MAPPING.items():
            if key in ing_l or key in lowered_text:
                signals.append({
                    "ingredient": ing,
                    "keyword": key,
                    "risk": info["risk"],
                    "reason": info.get("reason", "Contains %s" % key),
                    "severity": info.get("severity", "low"),
                    "matched_text": key,
                })
    # Also scan raw_text for any keywords not caught by ingredient split
    for key, info in KEYWORD_MAPPING.items():
        if key in lowered_text and not any(s["keyword"] == key for s in signals):
            signals.append({
                "ingredient": None,
                "keyword": key,
                "risk": info["risk"],
                "reason": info.get("reason", "Contains %s" % key),
                "severity": info.get("severity", "low"),
                "matched_text": key,
            })
    return signals


def apply_user_profile(profile: Any | None, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply profile-driven rules to signals and return structured warnings.

    Rules are modular and easy to extend.
    """
    warnings: List[Dict[str, Any]] = []

    # Helper to push warning uniquely
    def push(w: Dict[str, Any]):
        key = (w.get("warning"), w.get("ingredient"), w.get("reason"))
        if not any((x.get("warning"), x.get("ingredient"), x.get("reason")) == key for x in warnings):
            warnings.append(w)

    # First apply allergies: always HIGH
    allergies = []
    if profile and getattr(profile, "allergies", None):
        allergies = [a.strip().lower() for a in profile.allergies.split(",") if a.strip()]
    for s in signals:
        # Allergy matches -> high priority
        for allergy in allergies:
            if allergy and (allergy in (s.get("ingredient") or "").lower() or allergy in s.get("matched_text", "")):
                push({
                    "warning": f"Allergy risk: {allergy}",
                    "severity": "high",
                    "reason": f"Contains {s.get('matched_text')} which matches allergy {allergy}",
                    "ingredient": s.get("ingredient"),
                    "rule": "allergy_match",
                })

    # Condition rules
    conditions = []
    if profile and getattr(profile, "conditions", None):
        conditions = [c.strip().lower() for c in profile.conditions.split(",") if c.strip()] if isinstance(profile.conditions, str) else [c.strip().lower() for c in profile.conditions]

    for s in signals:
        risk = s.get("risk")
        # Diabetes + sugar
        if "diabetes" in conditions and risk == "diabetes":
            push({
                "warning": "Not recommended for diabetic users",
                "severity": "medium",
                "reason": s.get("reason"),
                "ingredient": s.get("ingredient"),
                "rule": "diabetes_sugar",
            })
        # Hypertension + sodium
        if "hypertension" in conditions and risk == "hypertension":
            push({
                "warning": "High sodium content — monitor if hypertensive",
                "severity": "medium",
                "reason": s.get("reason"),
                "ingredient": s.get("ingredient"),
                "rule": "hypertension_sodium",
            })
        # Lactose intolerance
        if "lactose_intolerance" in conditions or "lactose" in conditions:
            if risk == "lactose":
                push({
                    "warning": "Contains lactose — not suitable for lactose-intolerant users",
                    "severity": "high",
                    "reason": s.get("reason"),
                    "ingredient": s.get("ingredient"),
                    "rule": "lactose_intolerance",
                })

    # Generic rules: elevate severity for explicit high-risk keywords
    for s in signals:
        if s.get("severity") == "high":
            push({
                "warning": s.get("reason"),
                "severity": "high",
                "reason": s.get("reason"),
                "ingredient": s.get("ingredient"),
                "rule": "keyword_high",
            })

    # As a fallback, include mild warnings for medium signals
    for s in signals:
        if s.get("severity") == "medium":
            push({
                "warning": s.get("reason"),
                "severity": "medium",
                "reason": s.get("reason"),
                "ingredient": s.get("ingredient"),
                "rule": "keyword_medium",
            })

    # Sort warnings by severity: high, medium, low
    severity_order = {"high": 0, "medium": 1, "low": 2}
    warnings.sort(key=lambda w: severity_order.get(w.get("severity", "low"), 2))
    return warnings


def generate_personalized_sentences(warnings: List[Dict[str, Any]]) -> List[str]:
    """Create short sentences suitable for TTS from structured warnings."""
    sentences: List[str] = []
    for w in warnings:
        if w.get("severity") == "high":
            if w.get("ingredient"):
                sentences.append(f"Warning: {w.get('ingredient')} - {w.get('reason')}. {w.get('warning')}." )
            else:
                sentences.append(f"Warning: {w.get('reason')}. {w.get('warning')}." )
        else:
            sentences.append(f"Note: {w.get('reason')}. {w.get('warning')}." )
    return sentences
