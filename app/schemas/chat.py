"""
Chat message schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Request schema for sending a chat message"""
    content: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    reported_concerns: Optional[List[str]] = None


class ChatMessageResponse(BaseModel):
    """Response schema for chat message"""
    id: int
    role: str  # 'user' or 'assistant'
    content: str
    session_id: Optional[str] = None
    created_at: datetime
    
    # Context info
    current_scan_id: Optional[int] = None
    current_plan_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history"""
    messages: List[ChatMessageResponse]
    total: int
    session_id: Optional[str] = None


class ChatContextInfo(BaseModel):
    """Chat context information for AI"""
    user_id: int
    user_name: Optional[str] = None
    primary_concern: Optional[str] = None
    
    # Current treatment info
    has_active_plan: bool
    plan_locked: bool
    days_remaining: Optional[int] = None
    
    # Latest scan info
    has_recent_scan: bool
    latest_scan_date: Optional[datetime] = None
    latest_scores: Optional[Dict[str, float]] = None
    
    # Progress info
    score_trends: Optional[Dict[str, str]] = None  # improving, worsening, stable
