"""
Scan model
Represents facial image scans with metadata
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, func, Enum
from sqlalchemy.orm import relationship
from backend.db.session import Base
import enum


class ScanStatus(str, enum.Enum):
    """Scan processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageAngle(str, enum.Enum):
    """Image angle types"""
    FRONT = "front"
    LEFT = "left"
    RIGHT = "right"


class Scan(Base):
    """Facial scan model with AI analysis results"""
    
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Scan metadata
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False)
    scan_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Image storage (S3 keys)
    front_image_key = Column(String, nullable=False)
    left_image_key = Column(String, nullable=False)
    right_image_key = Column(String, nullable=False)
    
    # Image URLs (presigned or public)
    front_image_url = Column(String, nullable=True)
    left_image_url = Column(String, nullable=True)
    right_image_url = Column(String, nullable=True)
    
    # AI Analysis Results
    acne_score = Column(Float, nullable=True)  # 0-100
    redness_score = Column(Float, nullable=True)  # 0-100
    oiliness_score = Column(Float, nullable=True)  # 0-100
    dryness_score = Column(Float, nullable=True)  # 0-100
    
    # Additional metrics
    texture_score = Column(Float, nullable=True)
    pore_size_score = Column(Float, nullable=True)
    dark_spots_score = Column(Float, nullable=True)
    
    # Overall score (weighted average)
    overall_score = Column(Float, nullable=True)
    
    # Raw AI response (for debugging/audit)
    raw_analysis = Column(JSON, nullable=True)
    
    # Analysis metadata
    analysis_model_version = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(String, nullable=True)
    
    # Comparison flags
    is_baseline = Column(Boolean, default=False)  # First scan in treatment cycle
    week_number = Column(Integer, nullable=True)  # Week in current treatment cycle
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="scans")
    score_deltas = relationship("ScoreDelta", back_populates="scan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    @property
    def primary_scores(self):
        """Get primary skin concern scores"""
        return {
            "acne": self.acne_score,
            "redness": self.redness_score,
            "oiliness": self.oiliness_score,
            "dryness": self.dryness_score
        }
    
    @property
    def all_scores(self):
        """Get all available scores"""
        return {
            **self.primary_scores,
            "texture": self.texture_score,
            "pore_size": self.pore_size_score,
            "dark_spots": self.dark_spots_score,
            "overall": self.overall_score
        }
