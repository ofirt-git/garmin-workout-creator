from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from backend.app.models.workout import WorkoutType, StepType, DurationType, TargetType


class WorkoutStepBase(BaseModel):
    step_type: StepType
    description: Optional[str] = None
    duration_type: DurationType
    duration_value: Optional[float] = None
    target_type: TargetType = TargetType.OPEN
    target_value_low: Optional[float] = None
    target_value_high: Optional[float] = None
    repeat_times: Optional[int] = 1


class WorkoutStepResponse(WorkoutStepBase):
    id: UUID
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutCreate(BaseModel):
    prompt: str = Field(..., min_length=10, description="Natural language workout description")
    workout_type: WorkoutType = WorkoutType.RUNNING


class WorkoutResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    workout_type: WorkoutType
    original_prompt: str
    steps: List[WorkoutStepResponse] = []
    garmin_workout_id: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutUploadResponse(BaseModel):
    workout_id: UUID
    garmin_workout_id: str
    uploaded_at: datetime
    message: str
