"""
Chat schemas — matches Swift ChatMessage
"""
from pydantic import BaseModel
from typing import Optional


class ChatMessageSchema(BaseModel):
    id: str
    content: str
    isUser: bool
    timestamp: str  # ISO 8601


class ChatMessageRequest(BaseModel):
    content: str
    sessionId: Optional[str] = None
