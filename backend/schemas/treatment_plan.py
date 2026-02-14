"""
Treatment plan schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class PlanStatusEnum(str, Enum):
    """Plan status types"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ADJUSTED = "adjusted"
    CANCELLED = "cancelled"


class RoutineStep(BaseModel):
    """Single step in a routine"""
    step_number: int = Field(..., ge=1)
    product_type: str  # cleanser, toner, serum, moisturizer, sunscreen, etc.
    product_name: Optional[str] = None
    instructions: str
    wait_time_minutes: Optional[int] = Field(None, ge=0)


class TreatmentPlanCreate(BaseModel):
    """Request schema for creating treatment plan"""
    primary_concern: str = Field(..., pattern="^(acne|redness|dryness|oiliness)$")
    baseline_scan_id: int
    lock_duration_days: int = Field(14, ge=14, le=28)


class TreatmentPlanResponse(BaseModel):
    """Response schema for treatment plan"""
    id: int
    user_id: int
    status: PlanStatusEnum
    version: int
    
    # Concern and timeline
    primary_concern: str
    start_date: date
    planned_end_date: date
    lock_duration_days: int
    
    # Routines
    am_routine: List[Dict[str, Any]]
    pm_routine: List[Dict[str, Any]]
    
    # Additional info
    recommended_products: Optional[List[Dict[str, Any]]] = None
    instructions: Optional[str] = None
    warnings: Optional[str] = None
    
    # Lock status
    is_locked: bool
    days_remaining: int
    days_elapsed: int
    can_adjust: bool
    adjustment_reason: Optional[str] = None
    
    # References
    baseline_scan_id: Optional[int] = None
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TreatmentPlanUpdate(BaseModel):
    """Request schema for updating treatment plan"""
    adjustment_reason: str = Field(..., pattern="^(score_decline|severe_irritation|user_request)$")
    adjustment_notes: Optional[str] = None


class ProductRecommendation(BaseModel):
    """Product recommendation schema"""
    product_type: str
    recommended_ingredients: List[str]
    ingredients_to_avoid: List[str]
    application_tips: str
    example_products: Optional[List[str]] = None
