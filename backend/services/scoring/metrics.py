from pydantic import BaseModel, Field
from typing import List

class SkinMetrics(BaseModel):
    # scores are 0-100
    acne: int = Field(ge=0, le=100)
    redness: int = Field(ge=0, le=100)
    oiliness: int = Field(ge=0, le=100)
    dryness: int = Field(ge=0, le=100)
    texture: int = Field(ge=0, le=100)

    confidence: int = Field(ge=0, le=100)

    retake_required: bool
    retake_reasons: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
