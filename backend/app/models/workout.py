import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.app.db.base import Base
import enum


class WorkoutType(str, enum.Enum):
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    STRENGTH = "strength"
    OTHER = "other"


class StepType(str, enum.Enum):
    WARMUP = "warmup"
    INTERVAL = "interval"
    RECOVERY = "recovery"
    COOLDOWN = "cooldown"
    REPEAT = "repeat"


class DurationType(str, enum.Enum):
    TIME = "time"
    DISTANCE = "distance"
    CALORIES = "calories"
    HEART_RATE = "heart_rate"
    OPEN = "open"


class TargetType(str, enum.Enum):
    PACE = "pace"
    SPEED = "speed"
    HEART_RATE = "heart_rate"
    POWER = "power"
    CADENCE = "cadence"
    OPEN = "open"


class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Workout metadata
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    workout_type = Column(SQLEnum(WorkoutType), nullable=False, default=WorkoutType.RUNNING)

    # Original prompt and parsed data
    original_prompt = Column(Text, nullable=False)
    parsed_data = Column(JSONB, nullable=True)  # Store AI parsing results

    # Garmin integration
    garmin_workout_id = Column(String, nullable=True)  # ID from Garmin API
    uploaded_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workouts")
    steps = relationship("WorkoutStep", back_populates="workout", cascade="all, delete-orphan", order_by="WorkoutStep.order")

    def __repr__(self):
        return f"<WorkoutTemplate {self.name}>"


class WorkoutStep(Base):
    __tablename__ = "workout_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workout_templates.id"), nullable=False, index=True)

    # Step ordering
    order = Column(Integer, nullable=False)

    # Step details
    step_type = Column(SQLEnum(StepType), nullable=False)
    description = Column(String, nullable=True)

    # Duration
    duration_type = Column(SQLEnum(DurationType), nullable=False)
    duration_value = Column(Float, nullable=True)  # Seconds for time, meters for distance, etc.

    # Target
    target_type = Column(SQLEnum(TargetType), nullable=False, default=TargetType.OPEN)
    target_value_low = Column(Float, nullable=True)  # For zones/ranges
    target_value_high = Column(Float, nullable=True)  # For zones/ranges

    # Repeat configuration
    repeat_times = Column(Integer, nullable=True, default=1)
    repeat_steps = Column(JSONB, nullable=True)  # For nested repeat blocks

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("WorkoutTemplate", back_populates="steps")

    def __repr__(self):
        return f"<WorkoutStep {self.step_type} - Order {self.order}>"
