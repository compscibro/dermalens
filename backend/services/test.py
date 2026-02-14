#test

from services.vision.nanobanana_client import analyze_face_three_angles
from services.vision.normalize import clamp_metrics
from services.vision.validators import needs_retake
from services.scoring.trend import build_profile
from services.routine_engine.engine import build_plan

def run_ai(front_bytes: bytes, left_bytes: bytes | None, right_bytes: bytes | None, quiz: dict, priority: str):
    metrics = analyze_face_three_angles(front_bytes, left_bytes, right_bytes)
    metrics = clamp_metrics(metrics)

    if needs_retake(metrics):
        return {"retake_required": True, "metrics": metrics.model_dump()}

    profile = build_profile(metrics, quiz, priority)
    plan = build_plan(metrics, profile)

    return {
        "retake_required": False,
        "metrics": metrics.model_dump(),
        "plan": plan,
    }
