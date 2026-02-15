"""
Routine schemas — matches Swift RoutinePlan, RoutineStep
"""
from pydantic import BaseModel
from typing import List


class RoutineStepSchema(BaseModel):
    id: str
    order: int
    name: str
    description: str
    productSuggestion: str
    icon: str  # SF Symbol name


class RoutinePlanSchema(BaseModel):
    id: str
    date: str  # ISO 8601
    morningSteps: List[RoutineStepSchema]
    eveningSteps: List[RoutineStepSchema]
    weeklySteps: List[RoutineStepSchema]
