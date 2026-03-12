"""
Pydantic models for workout structure validation
Defines the standard workout JSON schema
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Union, List


class PaceTarget(BaseModel):
    """Target for pace-based workouts"""
    min_pace: int = Field(..., description="Minimum pace in seconds per distance unit")
    max_pace: int = Field(..., description="Maximum pace in seconds per distance unit")
    unit: Literal["seconds_per_km", "seconds_per_mile"]


class SpeedTarget(BaseModel):
    """Target for speed-based workouts"""
    min_speed: float = Field(..., description="Minimum speed")
    max_speed: float = Field(..., description="Maximum speed")
    unit: Literal["kph", "mph"]


class HeartRateTarget(BaseModel):
    """Target for heart rate-based workouts"""
    min_hr: Optional[int] = Field(None, description="Minimum heart rate in BPM")
    max_hr: Optional[int] = Field(None, description="Maximum heart rate in BPM")
    zone: Optional[int] = Field(None, ge=1, le=5, description="Heart rate zone 1-5")
    unit: Literal["bpm"] = "bpm"

    @field_validator('zone', 'min_hr', 'max_hr')
    @classmethod
    def validate_hr_target(cls, v, info):
        """Ensure either zone OR min/max_hr is provided, not both"""
        return v


class CadenceTarget(BaseModel):
    """Target for cadence-based workouts"""
    min_cadence: int = Field(..., description="Minimum cadence")
    max_cadence: int = Field(..., description="Maximum cadence")
    unit: Literal["spm", "rpm"]  # steps per minute or revolutions per minute


class PowerTarget(BaseModel):
    """Target for power-based workouts"""
    min_power: Optional[int] = Field(None, description="Minimum power in watts")
    max_power: Optional[int] = Field(None, description="Maximum power in watts")
    zone: Optional[int] = Field(None, ge=1, le=7, description="Power zone 1-7")
    unit: Literal["watts"] = "watts"


# Union type for all possible target values
TargetValue = Union[PaceTarget, SpeedTarget, HeartRateTarget, CadenceTarget, PowerTarget, None]


class WorkoutStep(BaseModel):
    """Represents a single step in a workout"""
    step_id: int = Field(..., description="Unique identifier for this step")
    step_type: Literal["warmup", "cooldown", "interval", "recovery", "rest", "repeat"]

    # Duration fields (None for repeat steps)
    duration_type: Optional[Literal["time", "distance", "lap_button", "open"]] = None
    duration_value: Optional[Union[int, float]] = None
    duration_unit: Optional[str] = None

    # Target fields
    target_type: Literal["open", "pace", "speed", "heart_rate", "cadence", "power"] = "open"
    target_value: Optional[TargetValue] = None

    # For repeat steps
    repeat_count: Optional[int] = Field(None, ge=1, description="Number of repetitions")
    steps: Optional[List['WorkoutStep']] = Field(None, description="Nested steps for repeat blocks")

    @field_validator('steps')
    @classmethod
    def validate_repeat_steps(cls, v, info):
        """Ensure repeat steps have nested steps"""
        if info.data.get('step_type') == 'repeat':
            if not v or len(v) == 0:
                raise ValueError("Repeat step must have nested steps")
        return v


class Workout(BaseModel):
    """Complete workout definition"""
    workout_name: str = Field(..., description="Name of the workout")
    sport_type: Literal["running", "cycling", "swimming", "other"]
    description: Optional[str] = Field(None, description="Optional workout description")
    steps: List[WorkoutStep] = Field(..., min_length=1, description="List of workout steps")

    def to_json(self, **kwargs) -> str:
        """Export workout as JSON string"""
        return self.model_dump_json(indent=2, **kwargs)

    @classmethod
    def from_json(cls, json_str: str) -> 'Workout':
        """Load workout from JSON string"""
        return cls.model_validate_json(json_str)
