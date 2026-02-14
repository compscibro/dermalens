"""
Chat router
Handles AI-powered conversations with users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.models.scan import Scan, ScanStatus
from app.models.treatment_plan import TreatmentPlan, PlanStatus
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatContextInfo
)
from app.core.security import get_current_active_user
from app.services.chat_ai.gemini_service import gemini_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send message to AI chat assistant
    
    Args:
        message_data: Chat message data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        AI response message
    """
    # Generate session ID if not provided
    session_id = message_data.session_id or str(uuid.uuid4())
    
    # Get conversation history
    history_result = await db.execute(
        select(ChatMessage)
        .where(
            and_(
                ChatMessage.user_id == current_user.id,
                ChatMessage.session_id == session_id
            )
        )
        .order_by(ChatMessage.created_at)
        .limit(20)  # Last 20 messages
    )
    history = history_result.scalars().all()
    
    # Build conversation history for AI
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]
    
    # Get current context
    context = await build_chat_context(current_user.id, db)
    
    # Save user message
    user_message = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=message_data.content,
        session_id=session_id,
        reported_concerns=message_data.reported_concerns,
        current_scan_id=context.latest_scan_date and await get_latest_scan_id(current_user.id, db),
        current_plan_id=context.has_active_plan and await get_active_plan_id(current_user.id, db)
    )
    
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # Generate AI response
    ai_response = await gemini_service.generate_response(
        user_message=message_data.content,
        conversation_history=conversation_history,
        context=context
    )
    
    # Save AI message
    assistant_message = ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=ai_response["content"],
        session_id=session_id,
        model_used=ai_response.get("model_used"),
        response_time_ms=ai_response.get("processing_time_ms"),
        contains_medical_advice=ai_response.get("contains_medical_advice", False),
        requires_follow_up=ai_response.get("requires_follow_up", False),
        current_scan_id=user_message.current_scan_id,
        current_plan_id=user_message.current_plan_id
    )
    
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    return ChatMessageResponse.model_validate(assistant_message)


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat message history
    
    Args:
        session_id: Optional session ID to filter by
        limit: Maximum number of messages to return
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Chat history
    """
    query = select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    
    if session_id:
        query = query.where(ChatMessage.session_id == session_id)
    
    query = query.order_by(desc(ChatMessage.created_at)).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    message_responses = [ChatMessageResponse.model_validate(msg) for msg in messages]
    
    return ChatHistoryResponse(
        messages=message_responses,
        total=len(message_responses),
        session_id=session_id
    )


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a chat session
    
    Args:
        session_id: Session ID to delete
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Success message
    """
    result = await db.execute(
        select(ChatMessage).where(
            and_(
                ChatMessage.user_id == current_user.id,
                ChatMessage.session_id == session_id
            )
        )
    )
    messages = result.scalars().all()
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    for message in messages:
        await db.delete(message)
    
    await db.commit()
    
    return {"message": f"Deleted {len(messages)} messages from session"}


async def build_chat_context(user_id: int, db: AsyncSession) -> ChatContextInfo:
    """
    Build context information for chat AI
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Chat context information
    """
    # Get user info
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one()
    
    # Get active treatment plan
    plan_result = await db.execute(
        select(TreatmentPlan).where(
            and_(
                TreatmentPlan.user_id == user_id,
                TreatmentPlan.status == PlanStatus.ACTIVE
            )
        )
    )
    active_plan = plan_result.scalar_one_or_none()
    
    # Get latest scan
    scan_result = await db.execute(
        select(Scan).where(
            and_(
                Scan.user_id == user_id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
        .order_by(desc(Scan.scan_date))
        .limit(1)
    )
    latest_scan = scan_result.scalar_one_or_none()
    
    # Get score trends (simplified)
    score_trends = None
    if latest_scan:
        score_trends = await calculate_trends(user_id, db)
    
    return ChatContextInfo(
        user_id=user_id,
        user_name=user.full_name,
        primary_concern=user.primary_concern,
        has_active_plan=active_plan is not None,
        plan_locked=active_plan.is_locked if active_plan else False,
        days_remaining=active_plan.days_remaining if active_plan else None,
        has_recent_scan=latest_scan is not None,
        latest_scan_date=latest_scan.scan_date if latest_scan else None,
        latest_scores=latest_scan.primary_scores if latest_scan else None,
        score_trends=score_trends
    )


async def calculate_trends(user_id: int, db: AsyncSession) -> dict:
    """
    Calculate score trends (simplified version)
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Dict of trends
    """
    # Get last 2 scans
    result = await db.execute(
        select(Scan).where(
            and_(
                Scan.user_id == user_id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
        .order_by(desc(Scan.scan_date))
        .limit(2)
    )
    scans = result.scalars().all()
    
    if len(scans) < 2:
        return {"overall": "insufficient_data"}
    
    current, previous = scans[0], scans[1]
    trends = {}
    
    for metric in ["acne", "redness", "oiliness", "dryness"]:
        curr_score = getattr(current, f"{metric}_score")
        prev_score = getattr(previous, f"{metric}_score")
        
        if curr_score and prev_score:
            delta = curr_score - prev_score
            if delta < -5:
                trends[metric] = "improving"
            elif delta > 5:
                trends[metric] = "worsening"
            else:
                trends[metric] = "stable"
    
    return trends


async def get_latest_scan_id(user_id: int, db: AsyncSession) -> Optional[int]:
    """Get latest scan ID"""
    result = await db.execute(
        select(Scan.id).where(
            and_(
                Scan.user_id == user_id,
                Scan.status == ScanStatus.COMPLETED
            )
        )
        .order_by(desc(Scan.scan_date))
        .limit(1)
    )
    scan_id = result.scalar_one_or_none()
    return scan_id


async def get_active_plan_id(user_id: int, db: AsyncSession) -> Optional[int]:
    """Get active plan ID"""
    result = await db.execute(
        select(TreatmentPlan.id).where(
            and_(
                TreatmentPlan.user_id == user_id,
                TreatmentPlan.status == PlanStatus.ACTIVE
            )
        )
    )
    plan_id = result.scalar_one_or_none()
    return plan_id
