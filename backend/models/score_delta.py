"""
ScoreDelta model
Tracks score changes between scans for progress monitoring
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from backend.db.session import Base


class ScoreDelta(Base):
    """Score change tracking between scans"""
    
    __tablename__ = "score_deltas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference scans
    current_scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    previous_scan_id = Column(Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True)
    
    # Metric being compared
    metric_name = Column(String, nullable=False)  # acne, redness, oiliness, dryness, etc.
    
    # Score values
    previous_score = Column(Float, nullable=True)
    current_score = Column(Float, nullable=False)
    delta = Column(Float, nullable=False)  # current - previous
    percent_change = Column(Float, nullable=True)  # ((current - previous) / previous) * 100
    
    # Delta interpretation
    improvement = Column(Boolean, nullable=False)  # True if improved, False if worsened
    is_significant = Column(Boolean, default=False)  # True if delta exceeds threshold
    
    # Context
    days_between_scans = Column(Integer, nullable=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", foreign_keys=[current_scan_id], back_populates="score_deltas")
    treatment_plan = relationship("TreatmentPlan", back_populates="score_deltas")
    
    def __repr__(self):
        return f"<ScoreDelta(metric={self.metric_name}, delta={self.delta:.2f})>"
    
    @property
    def delta_description(self):
        """Human-readable delta description"""
        direction = "improved" if self.improvement else "worsened"
        return f"{self.metric_name.title()} {direction} by {abs(self.percent_change):.1f}%"
