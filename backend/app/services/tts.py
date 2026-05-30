from __future__ import annotations

import hashlib
import wave
from pathlib import Path


def build_speech_text(
    expiry_status: str,
    ingredients: list[str],
    warnings: list[dict] | list[str],
    language: str = "en",
    label_details: list[dict] | None = None,
) -> str:
    """Build a TTS-friendly summary. Accepts structured warnings (list of dicts) or legacy list of strings.

    Structured warnings will be rendered into short sentences.
    """
    if language == "ur":
        base = "اس پروڈکٹ کا تجزیہ مکمل ہوگیا ہے۔"
    else:
        base = "This product analysis is complete."

    parts = [base]
    if expiry_status == "Expired":
        parts.append("The product is expired.")
    elif expiry_status == "Near Expiry":
        parts.append("The product is near expiry.")
    elif expiry_status == "Safe":
        parts.append("The product appears safe.")
    else:
        parts.append("Expiry date is unclear.")

    if label_details:
        label_sentences: list[str] = []
        for detail in label_details[:3]:
            field = str(detail.get("field") or "").replace("_", " ").strip()
            value = detail.get("value")
            if field and value:
                label_sentences.append(f"{field} {value}.")
        if label_sentences:
            parts.append("Detected label details: " + " ".join(label_sentences))

    if ingredients:
        parts.append(f"Key ingredients include {', '.join(ingredients[:3])}.")

    # Normalize warnings to list[str]
    warning_sentences: list[str] = []
    if warnings:
        if isinstance(warnings, list) and len(warnings) > 0 and isinstance(warnings[0], dict):
            # Structured warnings
            for w in warnings[:3]:
                ingredient = w.get("ingredient")
                reason = w.get("reason") or w.get("warning")
                if ingredient:
                    warning_sentences.append(f"This product contains {ingredient} and {reason}.")
                else:
                    warning_sentences.append(f"{reason}.")
        else:
            # Legacy list[str]
            warning_sentences = [str(x) for x in warnings[:3]]

    if warning_sentences:
        parts.append(" ".join(warning_sentences))
    return " ".join(parts)


def generate_audio_file(text: str, target_path: Path) -> str | None:
    try:
        import pyttsx3
    except Exception:
        return None

    target_path.parent.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
    wav_path = target_path.with_name(f"{target_path.stem}_{cache_key}.wav")
    if wav_path.exists():
        return str(wav_path)

    engine = pyttsx3.init()
    try:
        engine.setProperty("rate", 215)
        engine.setProperty("volume", 1.0)
    except Exception:
        pass
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()
    if wav_path.exists():
        return str(wav_path)
    return None


def create_silent_wav(target_path: Path, duration_ms: int = 100) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 16000
    frames = int(sample_rate * duration_ms / 1000)
    with wave.open(str(target_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * frames)
    return str(target_path)
