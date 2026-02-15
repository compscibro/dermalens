"""
Gemini Vision service for skin analysis.
Uses the new google.genai SDK with structured JSON output (response_schema).
Replaces the old google-generativeai manual-JSON-parsing approach.
"""
import os
import uuid
import logging
from typing import Optional

from google.genai import Client, types
from backend.services.scoring.metrics import SkinMetrics
from backend.core.config import settings

logger = logging.getLogger(__name__)

MODEL_ID = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")

SYSTEM_INSTRUCTIONS = """
You are a cosmetic skin-feature extractor.
Do NOT diagnose medical conditions. Do NOT claim diseases (e.g., rosacea, eczema).
Only describe visible features and output numeric scores from 0-100.

If image quality is insufficient (dark, blurry, face not centered, heavy shadows, extreme angle),
set:
- retake_required = true
- confidence <= 40
- include clear retake_reasons
Return ONLY JSON that matches the schema exactly.
"""


def _img_part(image_bytes: bytes, mime_type: str = "image/jpeg") -> types.Part:
    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )


def analyze_face_three_angles(
    front_bytes: bytes,
    left_bytes: Optional[bytes] = None,
    right_bytes: Optional[bytes] = None,
) -> SkinMetrics:
    """
    Send 1-3 face photos to Gemini and get back structured SkinMetrics.
    Uses response_schema so the model returns validated JSON directly.
    """
    client = Client(api_key=settings.GEMINI_API_KEY)

    parts = [
        types.Part(text="FRONT IMAGE:"),
        _img_part(front_bytes),
    ]

    if left_bytes:
        parts += [types.Part(text="LEFT IMAGE:"), _img_part(left_bytes)]

    if right_bytes:
        parts += [types.Part(text="RIGHT IMAGE:"), _img_part(right_bytes)]

    prompt = """
You will receive 1 to 3 images labeled FRONT IMAGE, LEFT IMAGE, RIGHT IMAGE.

Use ALL provided images to estimate cosmetic skin feature scores:
- acne, redness, oiliness, dryness, texture (each 0-100)

Also return:
- confidence (0-100): Higher when all 3 angles are provided and images are clear.
  If only 1 image is provided, lower confidence accordingly.
- retake_required (boolean)
- retake_reasons (list of short strings)
- notes (list of short, neutral, non-diagnostic observations)

Rules:
- Do NOT diagnose medical conditions and do NOT name diseases.
- If images are too dark/blurry/not centered/extreme angles or face not visible, set retake_required=true and confidence<=40.
Return ONLY JSON matching the schema.
"""
    parts.append(types.Part(text=prompt))

    resp = client.models.generate_content(
        model=MODEL_ID,
        contents=[types.Content(parts=parts)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema=SkinMetrics,
            temperature=0.2,
        ),
    )

    return resp.parsed


# ---------------------------------------------------------------------------
# Legacy adapter — converts SkinMetrics to the dict format that
# the existing API (scans.py, SkinScanSchema) expects.
# ---------------------------------------------------------------------------

def _color_for_score(score: float) -> str:
    """Map 0-100 score to colour bucket used by the iOS frontend."""
    if score <= 25:
        return "green"
    elif score <= 50:
        return "yellow"
    elif score <= 75:
        return "orange"
    return "red"


def metrics_to_legacy_analysis(metrics: SkinMetrics) -> dict:
    """
    Convert the new SkinMetrics model to the dict shape that
    SkinScanSchema / the iOS client expects:
        {scores: [{name, score, icon, color, id}], overallScore, summary}
    """
    metric_defs = [
        ("Acne", metrics.acne, "circle.fill"),
        ("Redness", metrics.redness, "flame.fill"),
        ("Oiliness", metrics.oiliness, "drop.fill"),
        ("Dryness", metrics.dryness, "sun.max.fill"),
        ("Texture", metrics.texture, "square.grid.3x3.topleft.filled"),
    ]

    scores = []
    total = 0
    for name, value, icon in metric_defs:
        total += value
        scores.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "score": float(value),
            "icon": icon,
            "color": _color_for_score(value),
        })

    # Overall skin health = inverse of average issue severity
    avg_issue = total / len(metric_defs)
    overall_score = round(100 - avg_issue, 1)

    # Build a short summary from notes or a generic one
    if metrics.notes:
        summary = " ".join(metrics.notes[:3])
    else:
        summary = (
            f"Skin analysis complete. Confidence: {metrics.confidence}%. "
            f"Key areas: acne {metrics.acne}, redness {metrics.redness}, "
            f"texture {metrics.texture}."
        )

    return {
        "scores": scores,
        "overallScore": overall_score,
        "summary": summary,
    }
