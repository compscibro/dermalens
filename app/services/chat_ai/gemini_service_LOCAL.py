"""
Gemini AI Chat Service - LOCAL TEST MODE
Returns mock responses for testing without real API
"""
import logging
from typing import List, Dict
from datetime import datetime
import asyncio

from app.schemas.chat import ChatContextInfo

logger = logging.getLogger(__name__)

class GeminiChatService:
    """Mock chat service for local testing"""
    
    def __init__(self):
        logger.info("🧪 Gemini in TEST MODE - using mock responses")
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: ChatContextInfo
    ) -> Dict:
        """Generate mock AI response"""
        logger.info(f"💬 Mock chat response for: {user_message[:50]}...")
        
        # Simulate API delay
        await asyncio.sleep(0.3)
        
        # Generate contextual mock response
        response = self._generate_mock_response(user_message, context)
        
        return {
            "content": response,
            "model_used": "mock-gemini-pro",
            "processing_time_ms": 300,
            "contains_medical_advice": False,
            "requires_follow_up": False
        }
    
    def _generate_mock_response(self, message: str, context: ChatContextInfo) -> str:
        """Generate contextual mock response"""
        message_lower = message.lower()
        
        # Greeting
        if any(word in message_lower for word in ['hi', 'hello', 'hey']):
            return f"Hello! I'm your DermaLens AI assistant. I can help you understand your skin analysis and treatment plan. How can I assist you today?"
        
        # Treatment plan questions
        if 'plan' in message_lower or 'routine' in message_lower:
            if context.has_active_plan:
                return f"You currently have an active treatment plan focusing on {context.primary_concern}. You have {context.days_remaining} days remaining in your lock period. Remember to follow your routine consistently for best results!"
            else:
                return "You don't have an active treatment plan yet. Complete a baseline scan to generate your personalized routine!"
        
        # Scan questions
        if 'scan' in message_lower or 'score' in message_lower:
            if context.has_recent_scan:
                scores_str = ", ".join([f"{k}: {v:.1f}" for k, v in (context.latest_scores or {}).items()])
                return f"Your latest scan shows: {scores_str}. These scores help track your progress over time!"
            else:
                return "You haven't completed a scan yet. Upload three facial images (front, left, right) to get started!"
        
        # Product questions
        if 'product' in message_lower or 'ingredient' in message_lower:
            return "For your skin concern, I recommend looking for products with ingredients like salicylic acid, niacinamide, and hyaluronic acid. Always patch test new products first!"
        
        # Progress questions
        if 'progress' in message_lower or 'improve' in message_lower:
            if context.score_trends:
                trends_str = ", ".join([f"{k}: {v}" for k, v in context.score_trends.items()])
                return f"Your progress trends: {trends_str}. Remember, skin improvement takes time and consistency!"
            else:
                return "Complete more scans to track your progress over time. We recommend weekly scans during your treatment period."
        
        # Irritation/concern
        if any(word in message_lower for word in ['irritation', 'burning', 'reaction', 'rash']):
            return "⚠️ If you're experiencing severe irritation, burning, or an allergic reaction, please stop using the products immediately and consult a dermatologist. Your safety is most important!"
        
        # Default helpful response
        return "I'm here to help you with your skincare journey! I can answer questions about your treatment plan, skin analysis scores, and general skincare guidance. What would you like to know?"

# Singleton instance
gemini_service = GeminiChatService()
