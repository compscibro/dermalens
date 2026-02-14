"""
Schemas package
All Pydantic models for request/response validation
"""
from backend.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordChange
)
from backend.schemas.scan import (
    ImageAngleEnum,
    ScanStatusEnum,
    PresignRequest,
    PresignResponse,
    ScanSubmitRequest,
    SkinScores,
    ScanResponse,
    ScanHistoryResponse,
    ScoreDeltaResponse
)
from backend.schemas.treatment_plan import (
    PlanStatusEnum,
    RoutineStep,
    TreatmentPlanCreate,
    TreatmentPlanResponse,
    TreatmentPlanUpdate,
    ProductRecommendation
)
from backend.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
    ChatContextInfo
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "PasswordChange",
    
    # Scan schemas
    "ImageAngleEnum",
    "ScanStatusEnum",
    "PresignRequest",
    "PresignResponse",
    "ScanSubmitRequest",
    "SkinScores",
    "ScanResponse",
    "ScanHistoryResponse",
    "ScoreDeltaResponse",
    
    # Treatment plan schemas
    "PlanStatusEnum",
    "RoutineStep",
    "TreatmentPlanCreate",
    "TreatmentPlanResponse",
    "TreatmentPlanUpdate",
    "ProductRecommendation",
    
    # Chat schemas
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ChatContextInfo",
]
