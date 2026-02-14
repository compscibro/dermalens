"""
Models package
Import all models here for Alembic auto-generation
"""
from backend.models.user import User
from backend.models.scan import Scan, ScanStatus, ImageAngle
from backend.models.score_delta import ScoreDelta
from backend.models.treatment_plan import TreatmentPlan, PlanStatus, AdjustmentReason
from backend.models.chat_message import ChatMessage

__all__ = [
    "User",
    "Scan",
    "ScanStatus",
    "ImageAngle",
    "ScoreDelta",
    "TreatmentPlan",
    "PlanStatus",
    "AdjustmentReason",
    "ChatMessage",
]
