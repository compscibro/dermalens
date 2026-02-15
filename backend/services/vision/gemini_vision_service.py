"""
Gemini Vision service for skin analysis
Replaces NanoBanana — sends face photos to Gemini multimodal API
"""
import json
import uuid
import logging
from PIL import Image
import io

import google.generativeai as genai

from backend.core.config import settings

logger = logging.getLogger(__name__)


class GeminiVisionService:
    """Analyze skin photos using Gemini Vision multimodal API."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def analyze_skin(
        self,
        front_image: bytes,
        left_image: bytes,
        right_image: bytes,
        concerns: dict,
    ) -> dict:
        """
        Analyze 3 face photos using Gemini Vision.
        Returns structured analysis matching SkinScanSchema.
        """
        images = [
            Image.open(io.BytesIO(front_image)),
            Image.open(io.BytesIO(left_image)),
            Image.open(io.BytesIO(right_image)),
        ]

        prompt = self._build_analysis_prompt(concerns)
        response = self.model.generate_content([prompt, *images])
        return self._parse_analysis(response.text)

    def generate_routine(self, analysis: dict, concerns: dict) -> dict:
        """
        Generate a personalized skincare routine based on analysis and concerns.
        Returns structured data matching RoutinePlanSchema.
        """
        prompt = self._build_routine_prompt(analysis, concerns)
        response = self.model.generate_content(prompt)
        return self._parse_routine(response.text)

    def _build_analysis_prompt(self, concerns: dict) -> str:
        primary = ", ".join(concerns.get("primaryConcerns", []))
        insecurity = concerns.get("biggestInsecurity", "Not specified")
        skin_type = concerns.get("skinType", "Not specified")
        sensitivity = concerns.get("sensitivityLevel", "Not specified")
        notes = concerns.get("additionalNotes", "None")

        return f"""You are a dermatological AI assistant analyzing facial skin photos.
You are given 3 photos: front face, left profile, right profile.

The user has reported the following concerns:
- Primary concerns: {primary}
- Biggest insecurity: {insecurity}
- Skin type: {skin_type}
- Sensitivity level: {sensitivity}
- Additional notes: {notes}

Analyze the images and return a JSON object with EXACTLY this structure:
{{
  "scores": [
    {{"name": "Acne", "score": <0-100 float>, "icon": "circle.fill", "color": "<green|yellow|orange|red>"}},
    {{"name": "Redness", "score": <0-100 float>, "icon": "flame.fill", "color": "<green|yellow|orange|red>"}},
    {{"name": "Oiliness", "score": <0-100 float>, "icon": "drop.fill", "color": "<green|yellow|orange|red>"}},
    {{"name": "Dryness", "score": <0-100 float>, "icon": "sun.max.fill", "color": "<green|yellow|orange|red>"}},
    {{"name": "Wrinkles", "score": <0-100 float>, "icon": "lines.measurement.horizontal", "color": "<green|yellow|orange|red>"}},
    {{"name": "Dark Spots", "score": <0-100 float>, "icon": "circle.dashed", "color": "<green|yellow|orange|red>"}},
    {{"name": "Pores", "score": <0-100 float>, "icon": "circle.grid.3x3.fill", "color": "<green|yellow|orange|red>"}},
    {{"name": "Texture", "score": <0-100 float>, "icon": "square.grid.3x3.topleft.filled", "color": "<green|yellow|orange|red>"}}
  ],
  "overallScore": <0-100 float>,
  "summary": "<2-3 sentence summary of skin condition>"
}}

Score meaning: Higher score = more of that issue detected (e.g., acne score 80 = significant acne).
Color rules: 0-25 = green (Good), 26-50 = yellow (Fair), 51-75 = orange (Needs Attention), 76-100 = red (Poor).
Overall score is a weighted health score where higher = better skin health.

Return ONLY valid JSON, no markdown formatting or code blocks."""

    def _build_routine_prompt(self, analysis: dict, concerns: dict) -> str:
        return f"""Based on this skin analysis and user concerns, generate a personalized skincare routine.

Skin Analysis: {json.dumps(analysis)}
User Concerns: {json.dumps(concerns)}

Return a JSON object with EXACTLY this structure:
{{
  "morningSteps": [
    {{"order": 1, "name": "step name", "description": "detailed instruction", "productSuggestion": "specific product name", "icon": "SF Symbol name"}},
    ...
  ],
  "eveningSteps": [...],
  "weeklySteps": [...]
}}

Guidelines:
- Morning routine: 4-5 steps (cleanser, serum/treatment, moisturizer, sunscreen)
- Evening routine: 4-6 steps (double cleanse, treatment, serum, moisturizer)
- Weekly routine: 1-3 steps (exfoliant, mask)
- Tailor products to the user's specific skin concerns and type
- Use real, purchasable product names

Use these SF Symbol icon names for steps:
- "drop.fill" for cleansers
- "sun.min.fill" for vitamin C / brightening
- "humidity.fill" for moisturizers
- "sun.max.trianglebadge.exclamationmark.fill" for sunscreen
- "testtube.2" for serums
- "moon.fill" for night treatments
- "sparkles" for exfoliants
- "face.dashed" for masks

Return ONLY valid JSON, no markdown formatting or code blocks."""

    def _parse_analysis(self, response_text: str) -> dict:
        """Parse Gemini's analysis response into structured data."""
        text = self._strip_code_fences(response_text)
        parsed = json.loads(text)

        # Add UUIDs to each metric
        for score in parsed["scores"]:
            score["id"] = str(uuid.uuid4())

        return parsed

    def _parse_routine(self, response_text: str) -> dict:
        """Parse Gemini's routine response into structured data."""
        text = self._strip_code_fences(response_text)
        parsed = json.loads(text)

        # Add UUIDs to each step
        for section in ["morningSteps", "eveningSteps", "weeklySteps"]:
            for step in parsed.get(section, []):
                step["id"] = str(uuid.uuid4())

        return parsed

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Strip markdown code fences from Gemini response."""
        text = text.strip()
        if text.startswith("```"):
            # Remove first line (```json or ```)
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


# Singleton instance
gemini_vision_service = GeminiVisionService()
