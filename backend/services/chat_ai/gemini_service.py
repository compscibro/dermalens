"""
Gemini AI Chat Service
Handles conversational AI for skincare guidance — simplified for S3-only backend.
Updated to use the new google.genai SDK.
"""
import logging
from typing import List, Dict, Optional

from google.genai import Client, types
from backend.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are DermaLens AI, a helpful skincare assistant. Your role is to:

1. Provide general skincare guidance and education
2. Help users understand their skin analysis results
3. Answer questions about their treatment plan
4. Encourage consistency with their skincare routine
5. Suggest when to rescan if concerns arise

Important Guidelines:
- You cannot diagnose medical conditions
- You cannot prescribe medications
- Always recommend consulting a dermatologist for serious concerns
- Be empathetic and supportive
- Focus on education and adherence

If a user reports severe symptoms (severe burning, bleeding, extreme reactions),
immediately suggest they stop the product and consult a healthcare provider."""


class GeminiChatService:
    """Service for Gemini AI chat interactions."""

    def __init__(self):
        self.client = Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = settings.GEMINI_MODEL

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: Optional[Dict] = None,
    ) -> str:
        """
        Generate AI response to user message.

        Args:
            user_message: User's message text
            conversation_history: Previous messages as list of
                {"role": "user"|"model", "parts": [text]}
            context: Optional dict with latest_analysis, routine, concerns

        Returns:
            AI response text
        """
        try:
            contextualized_prompt = self._build_prompt(user_message, context)

            # Build contents from conversation history (last 10 messages)
            history = conversation_history[-10:]
            contents = []
            for msg in history:
                role = msg.get("role", "user")
                parts_data = msg.get("parts", [])
                text_parts = []
                for p in parts_data:
                    if isinstance(p, str):
                        text_parts.append(types.Part(text=p))
                    elif isinstance(p, dict) and "text" in p:
                        text_parts.append(types.Part(text=p["text"]))
                if text_parts:
                    contents.append(types.Content(role=role, parts=text_parts))

            # Add the current user message
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=contextualized_prompt)],
                )
            )

            resp = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                ),
            )
            return resp.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return (
                "I'm having trouble processing your request right now. "
                "Please try again in a moment."
            )

    def _build_prompt(self, user_message: str, context: Optional[Dict]) -> str:
        """Build context-aware prompt."""
        parts = []

        if context:
            parts.append("Current Context:")
            if context.get("user_name"):
                parts.append(f"User: {context['user_name']}")
            if context.get("latest_analysis"):
                analysis = context["latest_analysis"]
                scores_str = ", ".join(
                    f"{s['name']}: {s['score']}" for s in analysis.get("scores", [])
                )
                parts.append(f"Latest Skin Scores: {scores_str}")
                parts.append(f"Overall Score: {analysis.get('overallScore', 'N/A')}")
                parts.append(f"Summary: {analysis.get('summary', 'N/A')}")
            if context.get("routine"):
                routine = context["routine"]
                morning_names = [s["name"] for s in routine.get("morningSteps", [])]
                evening_names = [s["name"] for s in routine.get("eveningSteps", [])]
                parts.append(f"Morning Routine: {', '.join(morning_names)}")
                parts.append(f"Evening Routine: {', '.join(evening_names)}")
            if context.get("concerns"):
                concerns = context["concerns"]
                parts.append(
                    f"Primary Concerns: {', '.join(concerns.get('primaryConcerns', []))}"
                )
                parts.append(
                    f"Skin Type: {concerns.get('skinType', 'Unknown')}"
                )
            parts.append("")

        parts.append(f"User Message: {user_message}")
        return "\n".join(parts)


# Singleton instance
gemini_service = GeminiChatService()
