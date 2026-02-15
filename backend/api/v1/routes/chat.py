"""
Chat router — Gemini-powered chat with S3 persistence.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from backend.schemas.chat import ChatMessageSchema, ChatMessageRequest
from backend.services.storage.s3_service import s3_service
from backend.services.chat_ai.gemini_service import gemini_service

router = APIRouter(prefix="/chat", tags=["Chat"])


def _load_latest_context(email: str) -> dict:
    """Load the latest analysis, routine, and concerns for chat context."""
    context: dict = {}

    # Get profile for user name
    profile = s3_service.get_json(s3_service.profile_key(email))
    if profile:
        context["user_name"] = profile.get("name")

    # Find latest scan
    prefixes = s3_service.list_prefixes(s3_service.scans_prefix(email))
    if not prefixes:
        return context

    # Collect scans with dates
    scans = []
    for prefix in prefixes:
        scan_id = prefix.rstrip("/").split("/")[-1]
        analysis = s3_service.get_json(s3_service.analysis_key(email, scan_id))
        if analysis:
            scans.append((scan_id, analysis))

    if not scans:
        return context

    # Sort by date descending, pick latest
    scans.sort(key=lambda x: x[1].get("date", ""), reverse=True)
    latest_scan_id, latest_analysis = scans[0]

    context["latest_analysis"] = latest_analysis

    routine = s3_service.get_json(s3_service.routine_key(email, latest_scan_id))
    if routine:
        context["routine"] = routine

    concerns = s3_service.get_json(s3_service.concerns_key(email, latest_scan_id))
    if concerns:
        context["concerns"] = concerns

    return context


@router.post("/message", response_model=ChatMessageSchema)
def send_message(
    body: ChatMessageRequest,
    email: str = Query(..., description="User email"),
):
    """Send a message and get an AI response."""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    session_id = body.sessionId or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Load existing conversation
    chat_key = s3_service.chat_key(email, session_id)
    messages = s3_service.get_json(chat_key) or []

    # Append user message
    user_msg = {
        "id": str(uuid.uuid4()),
        "content": body.content,
        "isUser": True,
        "timestamp": now,
    }
    messages.append(user_msg)

    # Build Gemini conversation history
    gemini_history = []
    for msg in messages[:-1]:  # Exclude the current user message (sent separately)
        role = "user" if msg["isUser"] else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # Load context from latest scan/routine
    context = _load_latest_context(email)

    # Generate AI response
    ai_text = gemini_service.generate_response(
        user_message=body.content,
        conversation_history=gemini_history,
        context=context,
    )

    # Append AI response
    ai_msg = {
        "id": str(uuid.uuid4()),
        "content": ai_text,
        "isUser": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    messages.append(ai_msg)

    # Persist conversation to S3
    s3_service.put_json(chat_key, messages)

    return ChatMessageSchema(**ai_msg)


@router.get("/history", response_model=List[ChatMessageSchema])
def get_chat_history(
    email: str = Query(..., description="User email"),
    sessionId: Optional[str] = None,
):
    """Get chat history for a session."""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    if sessionId:
        chat_key = s3_service.chat_key(email, sessionId)
        messages = s3_service.get_json(chat_key) or []
        return [ChatMessageSchema(**m) for m in messages]

    # If no session ID, list all sessions and return the latest
    prefixes = s3_service.list_keys(s3_service.chat_prefix(email))
    all_messages: List[dict] = []
    for key in prefixes:
        if key.endswith(".json"):
            msgs = s3_service.get_json(key)
            if msgs:
                all_messages.extend(msgs)

    # Sort by timestamp
    all_messages.sort(key=lambda m: m.get("timestamp", ""))
    return [ChatMessageSchema(**m) for m in all_messages]
