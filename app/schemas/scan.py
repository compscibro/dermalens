"""
Scan schemas for request/response validation
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ImageAngleEnum(str, Enum):
    """Image angle types"""
    FRONT = "front"
    LEFT = "left"
    RIGHT = "right"


class ScanStatusEnum(str, Enum):
    """Scan status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PresignRequest(BaseModel):
    """Request schema for presigned URL generation"""
    angle: ImageAngleEnum
    content_type: str = Field(..., pattern="^image/(jpeg|jpg|png)$")
    file_size: int = Field(..., gt=0, le=10485760)  # Max 10MB


class PresignResponse(BaseModel):
    """Response schema for presigned URL"""
    upload_url: str
    image_key: str
    expires_in: int


class ScanSubmitRequest(BaseModel):
    """Request schema for submitting a scan after upload"""
    front_image_key: str
    left_image_key: str
    right_image_key: str


class SkinScores(BaseModel):
    """Skin condition scores"""
    acne: Optional[float] = Field(None, ge=0, le=100)
    redness: Optional[float] = Field(None, ge=0, le=100)
    oiliness: Optional[float] = Field(None, ge=0, le=100)
    dryness: Optional[float] = Field(None, ge=0, le=100)
    texture: Optional[float] = Field(None, ge=0, le=100)
    pore_size: Optional[float] = Field(None, ge=0, le=100)
    dark_spots: Optional[float] = Field(None, ge=0, le=100)
    overall: Optional[float] = Field(None, ge=0, le=100)


class ScanResponse(BaseModel):
    """Response schema for scan data"""
    id: int
    user_id: int
    status: ScanStatusEnum
    scan_date: datetime
    
    # Image URLs
    front_image_url: Optional[str] = None
    left_image_url: Optional[str] = None
    right_image_url: Optional[str] = None
    
    # Scores
    scores: SkinScores
    
    # Metadata
    is_baseline: bool
    week_number: Optional[int] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm_with_scores(cls, scan):
        """Convert ORM model to schema with scores"""
        return cls(
            id=scan.id,
            user_id=scan.user_id,
            status=scan.status,
            scan_date=scan.scan_date,
            front_image_url=scan.front_image_url,
            left_image_url=scan.left_image_url,
            right_image_url=scan.right_image_url,
            scores=SkinScores(
                acne=scan.acne_score,
                redness=scan.redness_score,
                oiliness=scan.oiliness_score,
                dryness=scan.dryness_score,
                texture=scan.texture_score,
                pore_size=scan.pore_size_score,
                dark_spots=scan.dark_spots_score,
                overall=scan.overall_score
            ),
            is_baseline=scan.is_baseline,
            week_number=scan.week_number,
            confidence_score=scan.confidence_score,
            error_message=scan.error_message,
            created_at=scan.created_at
        )


class ScanHistoryResponse(BaseModel):
    """Response schema for scan history"""
    scans: list[ScanResponse]
    total: int
    page: int
    page_size: int


class ScoreDeltaResponse(BaseModel):
    """Response schema for score comparison"""
    metric_name: str
    previous_score: Optional[float]
    current_score: float
    delta: float
    percent_change: Optional[float]
    improvement: bool
    is_significant: bool
    days_between_scans: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)
