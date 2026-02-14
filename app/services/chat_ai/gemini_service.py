"""
Gemini AI Chat Service
Handles conversational AI for skincare guidance
"""
import google.generativeai as genai
import logging
from typing import List, Dict, Optional
from datetime import datetime

from app.core.config import settings
from app.schemas.chat import ChatContextInfo

logger = logging.getLogger(__name__)


class GeminiChatService:
    """Service for Gemini AI chat interactions"""
    
    def __init__(self):
        """Initialize Gemini client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for Gemini"""
        return """You are DermaLens AI, a helpful skincare assistant. Your role is to:

1. Provide general skincare guidance and education
2. Help users understand their skin analysis results
3. Answer questions about their treatment plan
4. Log concerns and symptoms (but do NOT modify treatment plans)
5. Encourage consistency with their locked routine
6. Suggest when to rescan if concerns arise

Important Guidelines:
- You cannot change treatment plans - they are locked for 2-4 weeks
- You cannot diagnose medical conditions
- You cannot prescribe medications
- Always recommend consulting a dermatologist for serious concerns
- Be empathetic and supportive
- Focus on education and adherence

If a user reports severe symptoms (severe burning, bleeding, extreme reactions), 
immediately suggest they stop the product and consult a healthcare provider.

For moderate concerns, note them and suggest a rescan at the appropriate time."""
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: ChatContextInfo
    ) -> Dict[str, any]:
        """
        Generate AI response to user message
        
        Args:
            user_message: User's message
            conversation_history: Previous messages
            context: Current user context (scan data, plan info, etc.)
        
        Returns:
            Dict with response and metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Build context-aware prompt
            contextualized_prompt = self._build_context_prompt(context, user_message)
            
            # Prepare chat history
            chat_history = self._format_history(conversation_history)
            
            # Start chat session
            chat = self.model.start_chat(history=chat_history)
            
            # Generate response
            response = await chat.send_message_async(contextualized_prompt)
            
            # Calculate tokens and time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Check for flags
            contains_medical_advice = self._check_medical_advice(response.text)
            requires_follow_up = self._check_follow_up_needed(response.text)
            
            return {
                "content": response.text,
                "model_used": settings.GEMINI_MODEL,
                "processing_time_ms": int(processing_time),
                "contains_medical_advice": contains_medical_advice,
                "requires_follow_up": requires_follow_up
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fallback response
            return {
                "content": "I'm having trouble processing your request right now. Please try again in a moment.",
                "model_used": settings.GEMINI_MODEL,
                "processing_time_ms": 0,
                "contains_medical_advice": False,
                "requires_follow_up": False,
                "error": str(e)
            }
    
    def _build_context_prompt(self, context: ChatContextInfo, user_message: str) -> str:
        """
        Build context-aware prompt with user's current state
        
        Args:
            context: User context information
            user_message: User's message
        
        Returns:
            Contextualized prompt
        """
        context_parts = []
        
        # User info
        context_parts.append(f"User: {context.user_name or 'User'}")
        if context.primary_concern:
            context_parts.append(f"Primary Concern: {context.primary_concern}")
        
        # Treatment plan status
        if context.has_active_plan:
            if context.plan_locked:
                context_parts.append(
                    f"Treatment Plan: LOCKED ({context.days_remaining} days remaining)"
                )
            else:
                context_parts.append("Treatment Plan: Can be adjusted")
        else:
            context_parts.append("Treatment Plan: No active plan")
        
        # Latest scan info
        if context.has_recent_scan and context.latest_scores:
            scores_str = ", ".join([
                f"{k}: {v:.1f}" for k, v in context.latest_scores.items()
            ])
            context_parts.append(f"Latest Scan Scores: {scores_str}")
        
        # Score trends
        if context.score_trends:
            trends_str = ", ".join([
                f"{k}: {v}" for k, v in context.score_trends.items()
            ])
            context_parts.append(f"Progress Trends: {trends_str}")
        
        # Combine context with user message
        full_context = "\n".join(context_parts)
        
        return f"""Current Context:
{full_context}

User Message: {user_message}

Please respond considering the above context. Remember:
- Treatment plans are locked and cannot be changed during the lock period
- Encourage adherence to the current routine
- Suggest rescanning if appropriate
- Be supportive and educational"""
    
    def _format_history(self, conversation_history: List[Dict[str, str]]) -> List[Dict]:
        """
        Format conversation history for Gemini
        
        Args:
            conversation_history: List of message dicts
        
        Returns:
            Formatted history for Gemini
        """
        formatted = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            formatted.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })
        return formatted
    
    def _check_medical_advice(self, response: str) -> bool:
        """
        Check if response contains medical advice flags
        
        Args:
            response: AI response text
        
        Returns:
            True if contains medical advice
        """
        medical_keywords = [
            "prescription",
            "medication",
            "diagnose",
            "treatment for",
            "you should take"
        ]
        return any(keyword in response.lower() for keyword in medical_keywords)
    
    def _check_follow_up_needed(self, response: str) -> bool:
        """
        Check if response suggests follow-up action
        
        Args:
            response: AI response text
        
        Returns:
            True if follow-up suggested
        """
        follow_up_keywords = [
            "consult",
            "see a dermatologist",
            "seek medical",
            "schedule",
            "follow up"
        ]
        return any(keyword in response.lower() for keyword in follow_up_keywords)


# Singleton instance
gemini_service = GeminiChatService()
