"""
Scan schemas — matches Swift SkinScan, SkinMetric, SkinConcernsForm, ScanRecord
"""
from pydantic import BaseModel
from typing import Optional, List


class SkinMetricSchema(BaseModel):
    id: str
    name: str
    score: float  # 0-100
    icon: str  # SF Symbol name
    color: str  # "green" | "yellow" | "orange" | "red"


class SkinScanSchema(BaseModel):
    id: str
    date: str  # ISO 8601
    frontImageName: Optional[str] = None
    leftImageName: Optional[str] = None
    rightImageName: Optional[str] = None
    scores: List[SkinMetricSchema]
    overallScore: float
    summary: str


class SkinConcernsFormSchema(BaseModel):
    primaryConcerns: List[str]
    biggestInsecurity: str
    skinType: str  # "Dry" | "Oily" | "Combination" | "Normal" | "Sensitive"
    sensitivityLevel: str  # "Low" | "Moderate" | "High"
    additionalNotes: str = ""


class ScanRecordSchema(BaseModel):
    id: str
    date: str  # ISO 8601
    overallScore: float
    thumbnailSystemName: str
    concerns: List[str]
