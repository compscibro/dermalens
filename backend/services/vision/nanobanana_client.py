import os

from dotenv import load_dotenv
load_dotenv()

from typing import Optional
from google.genai import Client, types
from services.scoring.metrics import SkinMetrics

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
    print("API KEY FOUND:", bool(os.getenv("GEMINI_API_KEY")))
    client = Client(api_key=os.getenv("GEMINI_API_KEY"))

    parts = [
        types.Part(text="Analyze these face images (front, left, right if provided)."),
        _img_part(front_bytes),
    ]
    if left_bytes:
        parts += [types.Part(text="LEFT ANGLE:"), _img_part(left_bytes)]
    if right_bytes:
        parts += [types.Part(text="RIGHT ANGLE:"), _img_part(right_bytes)]

    prompt = """
Return scores 0-100 for:
- acne, redness, oiliness, dryness, texture
Also return:
- confidence (0-100)
- retake_required boolean
- retake_reasons (list)
- notes (list of short neutral observations like "shine on T-zone", "scattered small blemishes")

Remember: cosmetic guidance only; no diagnosis.
"""

    resp = client.models.generate_content(
        model=MODEL_ID,
        contents=[types.Content(parts=parts)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema=SkinMetrics,  # pydantic schema
            temperature=0.2,
        ),
    )

    # The SDK will return JSON that matches SkinMetrics; parse it:
    # resp.parsed is supported when response_schema is provided (pydantic).
    return resp.parsed
