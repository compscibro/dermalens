"""
TreatmentPlan model
Represents locked skincare routines with AM/PM steps
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, func, Enum, Date
from sqlalchemy.orm import relationship
from backend.db.session import Base
import enum


class PlanStatus(str, enum.Enum):
    """Treatment plan status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ADJUSTED = "adjusted"
    CANCELLED = "cancelled"


class AdjustmentReason(str, enum.Enum):
    """Reasons for plan adjustment"""
    SCORE_DECLINE = "score_decline"
    SEVERE_IRRITATION = "severe_irritation"
    USER_REQUEST = "user_request"
    PLAN_COMPLETION = "plan_completion"


class TreatmentPlan(Base):
    """Treatment plan with locked routine"""
    
    __tablename__ = "treatment_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Plan metadata
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE, nullable=False)
    version = Column(Integer, default=1)  # Increments with each adjustment
    
    # Primary concern this plan addresses
    primary_concern = Column(String, nullable=False)  # acne, redness, dryness, oiliness
    
    # Lock period
    start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_end_date = Column(Date, nullable=True)
    lock_duration_days = Column(Integer, nullable=False)  # 14-28 days
    
    # Baseline scan reference
    baseline_scan_id = Column(Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True)
    
    # Routine structure (JSON)
    am_routine = Column(JSON, nullable=False)  # List of steps
    pm_routine = Column(JSON, nullable=False)  # List of steps
    
    # Product recommendations
    recommended_products = Column(JSON, nullable=True)  # List of product suggestions
    
    # Instructions and notes
    instructions = Column(String, nullable=True)
    warnings = Column(String, nullable=True)
    
    # Adjustment tracking
    can_adjust = Column(Boolean, default=False)
    adjustment_reason = Column(Enum(AdjustmentReason), nullable=True)
    adjustment_notes = Column(String, nullable=True)
    
    # Previous plan reference (for history)
    previous_plan_id = Column(Integer, ForeignKey("treatment_plans.id", ondelete="SET NULL"), nullable=True)
    
    # AI generation metadata
    generation_model = Column(String, nullable=True)
    generation_prompt = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="treatment_plans")
    baseline_scan = relationship("Scan", foreign_keys=[baseline_scan_id])
    score_deltas = relationship("ScoreDelta", back_populates="treatment_plan")
    
    def __repr__(self):
        return f"<TreatmentPlan(id={self.id}, concern={self.primary_concern}, status={self.status})>"
    
    @property
    def is_locked(self):
        """Check if plan is still in locked period"""
        from datetime import date
        if self.status != PlanStatus.ACTIVE:
            return False
        return date.today() < self.planned_end_date
    
    @property
    def days_remaining(self):
        """Days remaining in lock period"""
        from datetime import date
        if self.status != PlanStatus.ACTIVE:
            return 0
        delta = self.planned_end_date - date.today()
        return max(0, delta.days)
    
    @property
    def days_elapsed(self):
        """Days elapsed since plan start"""
        from datetime import date
        delta = date.today() - self.start_date
        return delta.days
