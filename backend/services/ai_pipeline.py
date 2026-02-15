"""
AI Pipeline Orchestrator
Runs the full analysis → normalize → retake check → profile → routine flow.
Based on teammate's run_ai() function, adapted for the main branch's import structure.
"""
from typing import Optional

from backend.services.vision.gemini_vision_service import (
    analyze_face_three_angles,
    metrics_to_legacy_analysis,
)
from backend.services.vision.normalize import clamp_metrics
from backend.services.vision.validators import needs_retake
from backend.services.scoring.trend import build_profile
from backend.services.routine_engine.engine import build_plan
from backend.services.routine_engine.routine_generator import generate_routine_from_plan


def run_ai(
    front_bytes: bytes,
    left_bytes: Optional[bytes],
    right_bytes: Optional[bytes],
    quiz: dict,
    priority: str,
    weeks_on_plan: int = 0,
) -> dict:
    """
    Full AI pipeline:
      1. Gemini vision → SkinMetrics
      2. Clamp scores 0-100
      3. Check retake requirement
      4. Build skin profile
      5. Build routine plan
      6. Convert to legacy format for API

    Returns a dict with:
      - retake_required: bool
      - metrics: dict (raw SkinMetrics)
      - analysis: dict (legacy format for SkinScanSchema — scores, overallScore, summary)
      - plan: dict (raw engine plan) — only if not retake
      - routine: dict (legacy format — morningSteps, eveningSteps, weeklySteps) — only if not retake
      - plan_locked: bool
      - lock_reason: str
    """
    # Step 1: Gemini vision analysis
    metrics = analyze_face_three_angles(front_bytes, left_bytes, right_bytes)

    # Step 2: Normalize / clamp
    metrics = clamp_metrics(metrics)

    # Step 3: Convert to legacy analysis format (always needed for the response)
    analysis = metrics_to_legacy_analysis(metrics)

    # Step 4: Check retake
    if needs_retake(metrics):
        return {
            "retake_required": True,
            "metrics": metrics.model_dump(),
            "analysis": analysis,
        }

    # Step 5: Build profile from metrics + user quiz
    profile = build_profile(metrics, quiz, priority)

    # Step 6: Build routine plan (local engine)
    plan = build_plan(metrics, profile)

    # Step 7: Convert plan to legacy routine format for the iOS client
    routine = generate_routine_from_plan(plan)

    # Step 8: Plan lock check
    plan_locked = weeks_on_plan < 2
    lock_reason = "Plan is locked for 2 weeks to assess changes." if plan_locked else ""

    return {
        "retake_required": False,
        "metrics": metrics.model_dump(),
        "analysis": analysis,
        "plan": plan,
        "routine": routine,
        "plan_locked": plan_locked,
        "lock_reason": lock_reason,
    }
